import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import List

from bank.generic.bank_statement_extractor import BankStatementExtractor
from bank.model.transaction import BankStatement, Transaction

class RevolutStatementExtractor(BankStatementExtractor):
    BANK_NOMINATION = "Revolut"
    def _parse_amount(self, amount_str: str) -> Decimal:
        try:
            return Decimal(amount_str.replace(',', '.').replace(' ', ''))
        except InvalidOperation:
            return Decimal(0)

    def extract_statement(self, csv_path: str) -> BankStatement:
        bank_statement = BankStatement(proof_document=csv_path)

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Parse dates
                transaction_date = datetime.fromisoformat(row["Started Date"])

                # Parse amounts and description
                amount = self._parse_amount(row["Amount"])
                income_amount = amount if amount > 0 else Decimal(0)
                expense_amount = abs(amount) if amount < 0 else Decimal(0)
                fee = self._parse_amount(row["Fee"])
                expense_amount += fee

                # Create transaction
                bank_statement.transactions.append(Transaction(
                    bank_nomination=RevolutStatementExtractor.BANK_NOMINATION,
                    transaction_date=transaction_date,
                    description=row["Description"],
                    expense_amount=expense_amount,
                    income_amount=income_amount,
                    proof_document=csv_path
                ))

        return bank_statement.compute_from_transactions()