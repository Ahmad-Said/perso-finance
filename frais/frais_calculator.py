import locale
import os
from datetime import datetime

import fitz  # PyMuPDF
import pandas as pd
from tqdm import tqdm

from const.const_gl import ConstGl
from frais.misc import special_frais
from frais.model.frais_details import FraisDetails
from frais.report import create_report
from frais.sncf.trip_achat_extractor import TripAchatExtractor
from frais.sncf.trip_extractor import TripExtractor
from frais.sncf.trip_voyage_extractor import TripVoyageExtractor
from util import pdf_merger, os_util, pdf_number
from util.result_file_cache import ResultFileCache


def extract_trip_frais_details(pdf_path: str, extractors: list[TripExtractor]) -> FraisDetails:
    frais_details = None
    # Open the PDF file
    with fitz.open(pdf_path) as pdf:
        # Loop through each page and extract text
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text = page.get_text()

            # Extract trip date
            for extractor in extractors:
                if extractor.is_supported(text):
                    frais_details = extractor.get_frais_details(text, pdf_path)
                    break

    if frais_details is None:
        raise ValueError(f"No supported extractor found for {pdf_path}")

    return frais_details


def extract_trip_frais_from_dir(pdf_dir: str, extractors: list[TripExtractor]) -> list[FraisDetails]:
    data = []
    # Iterate over each PDF file in the directory
    result_hasher = ResultFileCache()

    def extract_function(pdf_path_par: str) -> FraisDetails:
        return extract_trip_frais_details(pdf_path_par, extractors)

    def found_callback(frais_details_par: FraisDetails, pdf_path_par: str):
        frais_details_par.proof_document = pdf_path_par

    for filename in tqdm(os.listdir(pdf_dir), desc="Processing trip frais"):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            frais_details: FraisDetails = result_hasher.get_or_process_document(pdf_path, extract_function, found_callback)
            data.append(frais_details)
    return data


def get_printed_df(df: pd.DataFrame, total_amount: float) -> pd.DataFrame:
    # keep only and reorder columns
    printed_df = df[['payment_date_f', 'payment_day', 'comment', 'printed_proof', 'amount_paid', ]]

    # Add the total amount as the last row
    total_row = pd.DataFrame([{
        'payment_date_f': '',
        'payment_day': '',
        'comment': '',
        'printed_proof': 'Total',
        'amount_paid': total_amount}])
    printed_df = pd.concat([printed_df, total_row], ignore_index=True)

    # rename columns to french titles
    printed_df.columns = ['Date', 'Jour', 'Commentaire', 'Justificatif', 'Montant']

    return printed_df

def analyse_frais_details(frais_details: list[FraisDetails],
                          start_datetime: datetime,
                          end_datetime: datetime = None):
    total_amount = 0
    included_frais = []
    for frais in frais_details:
        if frais.payment_date and frais.payment_date >= start_datetime:
            if end_datetime and frais.payment_date > end_datetime:
                continue
            total_amount += frais.amount_paid
            included_frais.append(frais)

    # Create a DataFrame
    df = pd.DataFrame([frais.model_dump() for frais in included_frais])
    # format date as dddd dd/mm/yyyy
    payment_datetime_col = df['payment_date']
    df['payment_date_f'] = payment_datetime_col.dt.strftime('%d/%m/%Y')
    # format day as dddd capitalized (e.g., 'Vendredi')
    df['payment_day'] = payment_datetime_col.dt.strftime('%A').str.capitalize()

    # add a fake printed proof
    df['printed_proof'] = df['proof_document'].apply(lambda x: 'Page 12/321')

    # sort by payment date descending
    df = df.sort_values(by='payment_date', ascending=False)
    printed_df = get_printed_df(df, total_amount)
    # replace proof_document with starting page number
    summary_pdf = create_report.create_summary_pdf(printed_df, '31/12/2023')
    # merge all pdfs into a single one
    sorted_included_frais = sorted(included_frais, key=lambda x: x.payment_date, reverse=True)
    pdf_files = [summary_pdf] + [frais.proof_document for frais in sorted_included_frais]

    file_to_starting_page, total_pages = pdf_merger.predict_starting_page(pdf_files)

    df['printed_proof'] = df['proof_document'].apply(lambda x: f'Page {file_to_starting_page[x]}')
    printed_df = get_printed_df(df, total_amount)
    return printed_df, included_frais


def main():
    # Set locale to French (France)
    # locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    # Use the function on your PDF file
    # Example usage
    directory_path = ConstGl.PATH_TO_DATA_FRAIS_SNCF_TRIPS
    start_date = '29/10/2024'  # Specify the desired start date (day/month/year)
    start_datetime = datetime.strptime(start_date, '%d/%m/%Y')
    # Create a list of extractors
    extractors = [TripVoyageExtractor(), TripAchatExtractor()]
    # Extract trip frais details
    frais_details = extract_trip_frais_from_dir(directory_path, extractors)
    # Analyse frais details
    all_frais_details = frais_details + special_frais.read_special_frais().frais_details

    df, included_frais = analyse_frais_details(all_frais_details, start_datetime)

    # get max payment date
    end_datetime = max([frais.payment_date for frais in included_frais])
    end_datetime_str = end_datetime.strftime('%d/%m/%Y')

    summary_pdf = create_report.create_summary_pdf(df, end_datetime_str)

    # merge all pdfs into a single one
    sorted_included_frais = sorted(included_frais, key=lambda x: x.payment_date, reverse=True)
    pdf_files = [summary_pdf] + [frais.proof_document for frais in sorted_included_frais]

    aio_filename = f'aio_frais_{start_date}_{end_datetime_str}.pdf'.replace('/', '_')
    aio_merged_temp_pdf_path = os.path.join(ConstGl.TEMP_DIR, aio_filename)
    pdf_merger.merge_pdfs_with_bookmarks(pdf_files, aio_merged_temp_pdf_path)
    aio_merged_pdf_path = os.path.join(ConstGl.PATH_TO_DATA_FRAIS_RESULT, aio_filename)
    pdf_number.add_page_numbers(aio_merged_temp_pdf_path, aio_merged_pdf_path)
    os_util.open_with_associated_program(aio_merged_pdf_path)


if __name__ == '__main__':
    main()
