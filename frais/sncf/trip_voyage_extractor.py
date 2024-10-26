from datetime import datetime

from frais.sncf.trip_extractor import TripExtractor, TripDetails


class TripVoyageExtractor(TripExtractor):

    def is_supported(self, document_text):
        return 'JUSTIFICATIF DE VOYAGE' in document_text

    def extract_trip_details(self, document_text) -> TripDetails:
        trip_details = {
            'trip_date': None,
            'amount_paid': None,
            'start_destination': None,
            'end_destination': None
        }
        if 'Aller le' in document_text:
            date_line = document_text.split('Aller le')[1].split()[0]
            # date format 11/10/2024
            # convert to datetime object
            trip_details['trip_date'] = datetime.strptime(date_line, '%d/%m/%Y')

            # Extract amount paid
        if 'Montant du voyage' in document_text:
            amount_line = document_text.split('Montant du voyage')[1].split()[0].replace(',', '.')
            # example 12,50 -> 12.50
            # convert to decimal
            trip_details['amount_paid'] = float(amount_line)

            # Extract start and end destinations
        if 'Aller' in document_text:
            start_dest_line = document_text.split('De ')[1].split()[0]
            trip_details['start_destination'] = start_dest_line
        if 'à' in document_text:
            end_dest_line = document_text.split('à ')[1].split()[0]
            trip_details['end_destination'] = end_dest_line

        return TripDetails(**trip_details)