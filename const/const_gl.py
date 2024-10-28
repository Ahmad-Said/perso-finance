import os


class ConstGl:
    PERSON_FULL_NAME = 'FirstName LASTNAME'

    # Data paths architecture: convention over configuration
    # Data paths
    """
    Generic folder data architecture:
        -> data
            -> result
                -> aio_frais.pdf
                -> aio_banks.xlsx
            -> temp
                -> summary_table.html
                -> summary_table.pdf
            -> frais
                -> special_frais.json
                -> sncf
                    -> trip1.pdf
                    -> trip2.pdf
                    -> ...
            -> bank
                -> bnp
                    -> RLV_CHQ_23432423_2020-01-01.pdf
                    -> ...
                -> hello_bank
                -> revolut
                    -> account_statement_2020-01-01.csv
                -> sg
                    -> 2021-01-01.pdf
                    -> ...
    """
    PATH_TO_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    TEMP_DIR = os.path.join(PATH_TO_DATA, 'temp')
    SPECIAL_FRAIS_JSON = os.path.join(PATH_TO_DATA, 'frais', 'special_frais.json')

    """
    SNCF folder data architecture:
        -> sncf
            -> trips
                -> trip1.pdf
                -> trip2.pdf
                -> ...
    """
    PATH_TO_DATA_FRAIS_SNCF = os.path.join(PATH_TO_DATA, 'frais', 'sncf')
    PATH_TO_DATA_FRAIS_SNCF_TRIPS = os.path.join(PATH_TO_DATA_FRAIS_SNCF, 'trips')
    PATH_TO_DATA_FRAIS_RESULT = os.path.join(PATH_TO_DATA, 'result')

    PATH_TO_WK_HTML_TO_PDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

    # Bank data
    PATH_TO_BANK_DATA = os.path.join(PATH_TO_DATA, 'bank')
    PATH_TO_BANK_DATA_BNP = os.path.join(PATH_TO_BANK_DATA, 'bnp')
    PATH_TO_BANK_DATA_HELLO_BANK = os.path.join(PATH_TO_BANK_DATA, 'hello_bank')
    PATH_TO_BANK_DATA_REVOLUT = os.path.join(PATH_TO_BANK_DATA, 'revolut')
    PATH_TO_BANK_DATA_SG = os.path.join(PATH_TO_BANK_DATA, 'sg')
    PATH_TO_BANK_RESULT = os.path.join(PATH_TO_DATA, 'result')


def update_from_local():
    try:
        # Attempt to import ConstGlLocal
        from const.const_gl_local import ConstGlLocal
        # Update ConstGl with ConstGlLocal attributes
        for attr in dir(ConstGlLocal):
            if not attr.startswith("__"):
                if hasattr(ConstGl, attr) and getattr(ConstGl, attr) != getattr(ConstGlLocal, attr):
                    print(f"{attr} ->  {getattr(ConstGlLocal, attr)}")
                    setattr(ConstGl, attr, getattr(ConstGlLocal, attr))
    except ImportError as e:
        # If const_gl_local.py does not exist, use ConstGl as is
        pass
    setup_dirs()

def setup_dirs():
    dirs = [
        ConstGl.PATH_TO_DATA,
        ConstGl.TEMP_DIR,
        ConstGl.PATH_TO_DATA_FRAIS_SNCF,
        ConstGl.PATH_TO_DATA_FRAIS_SNCF_TRIPS,
        ConstGl.PATH_TO_DATA_FRAIS_RESULT,
        ConstGl.PATH_TO_BANK_DATA,
        ConstGl.PATH_TO_BANK_DATA_BNP,
        ConstGl.PATH_TO_BANK_DATA_HELLO_BANK,
        ConstGl.PATH_TO_BANK_DATA_REVOLUT,
        ConstGl.PATH_TO_BANK_DATA_SG,
        ConstGl.PATH_TO_BANK_RESULT,
    ]

    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

update_from_local()
