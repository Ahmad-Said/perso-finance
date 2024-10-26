import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pdfplumber

from bank.model.transaction import BankStatement, Transaction


class BNPStatementExtractor:
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

    def _extract_start_end_dates(self, text: str) -> tuple[datetime, datetime]:
        # pattern example: ".... du 6 janvier 2024 au 6 février 2024 ...."
        start_date = None
        end_date = None
        pattern_date = r"du (\d{1,2}) (\w+) (\d{4}) au (\d{1,2}) (\w+) (\d{4})"
        # special character like 'é' is not recognized by the regex pattern
        text = text.replace('Ø', 'é')
        # aoßt -> août
        text = text.replace('ß', 'û')

        match = re.search(pattern_date, text)
        if match:
            start_day, start_month, start_year, end_day, end_month, end_year = match.groups()
            start_month = self.french_months.get(start_month)
            end_month = self.french_months.get(end_month)
            start_date = datetime(int(start_year), int(start_month), int(start_day))
            end_date = datetime(int(end_year), int(end_month), int(end_day))

        return start_date, end_date

    TABLE_COLUMNS_INDEX = {
        "date_month_dot_day": 0,
        "description": 1,
        "date_repeated": 2,
        "expense_amount": 3,
        "income_amount": 4,
    }
    @staticmethod
    def is_decimal(s) -> tuple[bool, Decimal]:
        s = s.replace(',', '.').replace(' ', '')
        if not s:
            return False, Decimal(0)
        try:
            value = Decimal(s)
            return True, value
        except InvalidOperation:
            return False, Decimal(0)

    def extract_statement(self, pdf_path: str) -> BankStatement:
        table_settings = {
            "text_x_tolerance": 2,
            "vertical_strategy": "lines",
            "horizontal_strategy": "text",
            "snap_y_tolerance": 0,
            "intersection_x_tolerance": 15,
        }

        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text(x_tolerance=2)
            start_date, end_date = self._extract_start_end_dates(first_page_text)
            first_date_month = start_date.strftime("%m")
            second_date_month = end_date.strftime("%m")
            initial_credit_balance = 0
            final_credit_balance = 0
            total_income = 0
            total_expense = 0
            transactions: list[Transaction] = []
            for page in pdf.pages:
                table = page.extract_table(table_settings)
                if not table:
                    continue
                start_extracting = False
                for row in table:
                    if row[self.TABLE_COLUMNS_INDEX["date_month_dot_day"]] == "Date":
                        # header row
                        continue
                    # if all columns are empty, skip the row
                    if all(not cell for cell in row):
                        continue

                    date_month_dot_day = row[self.TABLE_COLUMNS_INDEX["date_month_dot_day"]]
                    transaction_date = None

                    if date_month_dot_day and len(date_month_dot_day.strip()) == 5:
                        date_month_dot_day = date_month_dot_day.split('.')
                        day = date_month_dot_day[0]
                        month = date_month_dot_day[1]
                        if month == first_date_month:
                            year = start_date.year
                        else:
                            year = end_date.year
                        transaction_date = datetime(year, int(month), int(day))

                    description = row[self.TABLE_COLUMNS_INDEX["description"]]
                    expense_amount_str = row[self.TABLE_COLUMNS_INDEX["expense_amount"]]
                    is_outgoing, expense_amount = BNPStatementExtractor.is_decimal(expense_amount_str)
                    incoming_amount_str = row[self.TABLE_COLUMNS_INDEX["income_amount"]]
                    is_incoming, incoming_amount = BNPStatementExtractor.is_decimal(incoming_amount_str)

                    if not transaction_date and is_incoming and description:
                        # first row of the table
                        # example: "SOLDE CREDITEUR AU 06.01.2024"
                        initial_credit_balance = incoming_amount
                    elif not transaction_date and date_month_dot_day == 'TOTAL DES OPERATIONS':
                        # last row of the table
                        # ['TOTAL DES OPERATIONS', None, None, '3 003,79', '250,88']
                        total_expense_str = row[self.TABLE_COLUMNS_INDEX["expense_amount"]]
                        _, total_expense = self.is_decimal(total_expense_str)
                        total_income_str = row[self.TABLE_COLUMNS_INDEX["income_amount"]]
                        _, total_income = self.is_decimal(total_income_str)
                    elif not transaction_date and 'SOLDE CREDITEUR' in date_month_dot_day:
                        # row with only the final credit balance
                        # ['SOLDE CREDITEUR AU 06.02.2024', None, None, '', '763,61']
                        final_credit_balance_str = row[self.TABLE_COLUMNS_INDEX["income_amount"]]
                        _, final_credit_balance = self.is_decimal(final_credit_balance_str)
                    elif is_incoming or is_outgoing:
                        transactions.append(Transaction(
                            transaction_date=transaction_date,
                            description=description,
                            expense_amount=expense_amount,
                            income_amount=incoming_amount,
                            proof_document=pdf_path
                        ))
                    elif description:
                        transactions[-1].description += description

        return BankStatement(
            transactions=transactions,
            total_expense=total_expense,
            total_income=total_income,
            initial_credit_balance=initial_credit_balance,
            final_credit_balance=final_credit_balance,
            start_date=start_date,
            end_date=end_date,
            proof_document=pdf_path
        )


if __name__ == '__main__':
    bnp_extractor = BNPStatementExtractor()
    bank_statement = bnp_extractor.extract_statement('RLV_CHQ_300040018600002709179_20240206.pdf')
    bank_statement.validate_statement()
    print(bank_statement)
