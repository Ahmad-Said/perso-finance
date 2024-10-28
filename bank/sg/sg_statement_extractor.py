import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

import pdfplumber

from bank.generic.bank_statement_extractor import BankStatementExtractor
from bank.model.transaction import BankStatement, Transaction
from const.const_gl import ConstGl
from util import numeric_parser


class SGStatementExtractor(BankStatementExtractor):
    BANK_NOMINATION = "SG"

    TABLE_COLUMNS_INDEX = {
        "dd_mm_yyy": 0,
        "date_repeated": 1,
        "description": 2,
        "expense_amount": -2,
        "income_amount": -1,
    }

    TABLE_SETTINGS = {
        "text_x_tolerance": 2, "vertical_strategy": "lines",
        "horizontal_strategy": "text", "snap_y_tolerance": 0,
        "intersection_x_tolerance": 15
    }

    def _extract_start_end_dates(self, text: str) -> tuple[datetime, datetime]:
        # pattern example: ".... du 09/04/2021 au 06/05/2021 ...."
        start_date = None
        end_date = None
        pattern_date = r"du (\d{2})/(\d{2})/(\d{4}) au (\d{2})/(\d{2})/(\d{4})"
        match = re.search(pattern_date, text)
        if match:
            start_date = datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            end_date = datetime(int(match.group(6)), int(match.group(5)), int(match.group(4)))

        return start_date, end_date

    def _extract_final_credit_balance_from_text(self, text: str) -> Optional[Decimal]:
        # pattern example: "NOUVEAU SOLDE AU 06/05/2021 + 26.198,31"
        pattern = r"NOUVEAU SOLDE AU \d{2}/\d{2}/\d{4} \+? ([\d.,]+)"
        match = re.search(pattern, text)
        if match:
            return numeric_parser.is_decimal(match.group(1))[1]
        return None

    def _extract_final_credit_balance(self, pdf) -> Decimal:
        # extract the final credit balance from final page
        for i in range(len(pdf.pages) - 1, -1, -1):
            page = pdf.pages[i]
            text = page.extract_text(x_tolerance=2)
            credit_balance = self._extract_final_credit_balance_from_text(text)
            if credit_balance:
                return credit_balance
        return Decimal(0)

    def _parse_transaction_date(self, date_str) -> Optional[datetime]:
        # transaction date example: 06/05/2021
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return None

    def extract_statement(self, pdf_path: str) -> BankStatement:
        bank_statement = BankStatement(proof_document=pdf_path)
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text(x_tolerance=2)
            bank_statement.start_date, bank_statement.end_date = self._extract_start_end_dates(first_page_text)
            for page in pdf.pages:
                tables = page.extract_tables(SGStatementExtractor.TABLE_SETTINGS)
                for table in tables:
                    if not table or len(table[0]) < len(self.TABLE_COLUMNS_INDEX):
                        continue
                    for row in table:
                        # if all columns are empty, skip the row
                        if all(not cell for cell in row):
                            continue
                        self.process_row(row, bank_statement)
            # extract the final credit balance from final page
            bank_statement.final_credit_balance = self._extract_final_credit_balance(pdf)

        return bank_statement

    def process_row(self, row: list, bank_statement: BankStatement):
        transaction_date_str = row[self.TABLE_COLUMNS_INDEX["dd_mm_yyy"]]
        transaction_date = self._parse_transaction_date(transaction_date_str)

        description = row[self.TABLE_COLUMNS_INDEX["description"]]
        expense_amount_str = row[self.TABLE_COLUMNS_INDEX["expense_amount"]]
        is_outgoing, expense_amount = numeric_parser.is_decimal(expense_amount_str)
        incoming_amount_str = row[self.TABLE_COLUMNS_INDEX["income_amount"]]
        is_incoming, incoming_amount = numeric_parser.is_decimal(incoming_amount_str)

        if transaction_date_str and 'SOLDE PRÉCÉDENT AU' in transaction_date_str:
            # first row of the table
            # example: "SOLDE PRÉCÉDENT AU 09/04/2021 - 4.908,39"
            bank_statement.initial_credit_balance = incoming_amount
        elif not transaction_date and is_incoming and is_outgoing:
            # last row of the table
            # [None, None, None, '740,29', '4.168,68']
            bank_statement.total_expense = expense_amount
            bank_statement.total_income = incoming_amount
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
    bank_extractor = SGStatementExtractor()
    pdf_file = os.listdir(ConstGl.PATH_TO_BANK_DATA_SG)[0]
    pdf_file = os.path.join(ConstGl.PATH_TO_BANK_DATA_SG, pdf_file)
    bank_statement = bank_extractor.extract_statement(pdf_file)
    bank_statement.validate_statement()
    print(bank_statement)

if __name__ == '__main__':
    main()
