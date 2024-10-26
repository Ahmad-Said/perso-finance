from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_date: datetime
    description: str
    expense_amount: Decimal
    income_amount: Decimal
    proof_document: str


class BankStatement(BaseModel):
    transactions: list[Transaction]
    total_expense: Decimal
    total_income: Decimal
    initial_credit_balance: Decimal
    final_credit_balance: Decimal
    start_date: datetime
    end_date: datetime
    proof_document: str

    def validate_statement(self):
        # validate the statement
        total_income = sum([transaction.income_amount for transaction in self.transactions])
        total_expense = sum([transaction.expense_amount for transaction in self.transactions])
        assert self.total_income == total_income, f"Total income mismatch: {self.total_income} != {total_income}"
        assert self.total_expense == total_expense, f"Total expense mismatch: {self.total_expense} != {total_expense}"
        assert self.final_credit_balance == self.initial_credit_balance + total_income - total_expense, \
            f"Final credit balance mismatch: {self.final_credit_balance} != {self.initial_credit_balance + total_income - total_expense}"