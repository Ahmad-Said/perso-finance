import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pdfplumber

from bank.generic.bank_statement_extractor import BankStatementExtractor
from bank.model.transaction import BankStatement, Transaction
from util import numeric_parser


class BNPStatementExtractor(BankStatementExtractor):
    BANK_NOMINATION = "BNP"
    french_months = {
        "janvier": "01",
        "février": "02",
        "mars": "03",
        "avril": "04",
        "mai": "05",
        "juin": "06",
        "juillet": "07",
        "août": "08",
        "septembre": "09",
        "octobre": "10",
        "novembre": "11",
        "décembre": "12"
    }

    TABLE_COLUMNS_INDEX = {
        "date_month_dot_day": 0,
        "description": 1,
        "date_repeated": 2,
        "expense_amount": 3,
        "income_amount": 4,
    }

    TABLE_SETTINGS = {
        "text_x_tolerance": 2, "vertical_strategy": "lines",
        "horizontal_strategy": "text", "snap_y_tolerance": 0,
        "intersection_x_tolerance": 15
    }

    def _normalize_text(self, text: str) -> str:
        # special character like 'é' is not recognized by the regex pattern
        text = text.replace('Ø', 'é')
        # aoßt -> août
        text = text.replace('ß', 'û')
        return text

    def _extract_start_end_dates(self, text: str) -> tuple[datetime, datetime]:
        # pattern example: ".... du 6 janvier 2024 au 6 février 2024 ...."
        start_date = None
        end_date = None
        pattern_date = r"du (\d{1,2}) (\w+) (\d{4}) au (\d{1,2}) (\w+) (\d{4})"
        text = self._normalize_text(text)
        match = re.search(pattern_date, text)
        if match:
            start_day, start_month, start_year, end_day, end_month, end_year = match.groups()
            start_month = self.french_months.get(start_month)
            end_month = self.french_months.get(end_month)
            start_date = datetime(int(start_year), int(start_month), int(start_day))
            end_date = datetime(int(end_year), int(end_month), int(end_day))

        return start_date, end_date

    def _parse_transaction_date(self, date_str, start_date, end_date) -> datetime:
        if not date_str or len(date_str.strip()) != 5:
            return None
        day, month = date_str.split('.')
        year = start_date.year if month == start_date.strftime("%m") else end_date.year
        return datetime(year, int(month), int(day))

    def extract_statement(self, pdf_path: str) -> BankStatement:
        bank_statement = BankStatement(proof_document=pdf_path)
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text(x_tolerance=2)
            start_date, end_date = self._extract_start_end_dates(first_page_text)
            bank_statement.start_date = start_date
            bank_statement.end_date = end_date
            for page in pdf.pages:
                table = page.extract_table(BNPStatementExtractor.TABLE_SETTINGS)
                if not table:
                    continue
                for row in table:
                    if row[self.TABLE_COLUMNS_INDEX["date_month_dot_day"]] == "Date":
                        # header row
                        continue
                    # if all columns are empty, skip the row
                    if all(not cell for cell in row):
                        continue
                    self.process_row(row, bank_statement, start_date, end_date)
        return bank_statement

    def process_row(self, row: list, bank_statement: BankStatement, start_date: datetime, end_date: datetime):
        date_month_dot_day = row[self.TABLE_COLUMNS_INDEX["date_month_dot_day"]]
        transaction_date = self._parse_transaction_date(date_month_dot_day, start_date, end_date)

        description = row[self.TABLE_COLUMNS_INDEX["description"]]
        expense_amount_str = row[self.TABLE_COLUMNS_INDEX["expense_amount"]]
        is_outgoing, expense_amount = numeric_parser.is_decimal(expense_amount_str)
        incoming_amount_str = row[self.TABLE_COLUMNS_INDEX["income_amount"]]
        is_incoming, incoming_amount = numeric_parser.is_decimal(incoming_amount_str)

        if not transaction_date and is_incoming and description:
            # first row of the table
            # example: "SOLDE CREDITEUR AU 06.01.2024"
            bank_statement.initial_credit_balance = incoming_amount
        elif not transaction_date and date_month_dot_day == 'TOTAL DES OPERATIONS':
            # last row of the table
            # ['TOTAL DES OPERATIONS', None, None, '3 003,79', '250,88']
            bank_statement.total_expense = expense_amount
            bank_statement.total_income = incoming_amount
        elif not transaction_date and 'SOLDE CREDITEUR' in date_month_dot_day:
            # row with only the final credit balance
            # ['SOLDE CREDITEUR AU 06.02.2024', None, None, '', '763,61']
            bank_statement.final_credit_balance = incoming_amount
        elif is_incoming or is_outgoing:
            bank_statement.transactions.append(Transaction(
                bank_nomination=self.BANK_NOMINATION,
                transaction_date=transaction_date,
                description=description,
                expense_amount=expense_amount,
                income_amount=incoming_amount,
                proof_document=bank_statement.proof_document
            ))
        elif description:
            bank_statement.transactions[-1].description += description


def main():
    bnp_extractor = BNPStatementExtractor()
    bank_statement = bnp_extractor.extract_statement('RLV_CHQ_300040018600002709179_20240206.pdf')
    bank_statement.validate_statement()
    print(bank_statement)


if __name__ == '__main__':
    main()
