from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from bank.model.transaction_category import TransactionCategory


class Transaction(BaseModel):
    bank_nomination: str
    transaction_date: datetime
    description: str
    expense_amount: Decimal
    income_amount: Decimal

    # computed properties
    transaction_category: TransactionCategory = TransactionCategory.MISCELLANEOUS_OTHER
    proof_document: str

    def get_signature(self):
        formatted_date = self.transaction_date.strftime("%Y-%m-%d")
        return f"{self.bank_nomination}_{formatted_date}_{self.description}_{self.expense_amount}_{self.income_amount}"


class BankStatement(BaseModel):
    transactions: list[Transaction] = []
    total_expense: Decimal = Decimal(0)
    total_income: Decimal = Decimal(0)
    initial_credit_balance: Decimal = Decimal(0)
    final_credit_balance: Decimal = Decimal(0)
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(1970, 1, 1)
    proof_document: str = ""

    def validate_statement(self):
        # validate the statement
        total_income = sum([transaction.income_amount for transaction in self.transactions])
        total_expense = sum([transaction.expense_amount for transaction in self.transactions])
        assert self.total_income == total_income, f"Total income mismatch: {self.total_income} != {total_income}"
        assert self.total_expense == total_expense, f"Total expense mismatch: {self.total_expense} != {total_expense}"
        assert self.final_credit_balance == self.initial_credit_balance + total_income - total_expense, \
            f"Final credit balance mismatch: {self.final_credit_balance} != {self.initial_credit_balance + total_income - total_expense}"

    def compute_from_transactions(self):
        self.total_income = sum([transaction.income_amount for transaction in self.transactions])
        self.total_expense = sum([transaction.expense_amount for transaction in self.transactions])
        self.final_credit_balance = self.initial_credit_balance + self.total_income - self.total_expense
        self.start_date = min([transaction.transaction_date for transaction in self.transactions])
        self.end_date = max([transaction.transaction_date for transaction in self.transactions])
        return self