from enum import Enum

from pydantic import BaseModel, field_serializer, ConfigDict


class TransactionCategory(Enum):
    GROCERIES ="GROCERIES"
    DINING_ENTERTAINMENT = "DINING_ENTERTAINMENT"
    UTILITIES = "UTILITIES"
    TAXES = "TAXES"
    SALARY ="SALARY"
    HOUSING ="HOUSING"
    TRANSPORTATION ="TRANSPORTATION"
    HEALTH_WELLNESS = "HEALTH_WELLNESS"
    ONLINE_SHOPPING = "ONLINE_SHOPPING"
    TRAVEL ="TRAVEL"
    EDUCATION_PROFESSIONAL = "EDUCATION_PROFESSIONAL"
    PERSONAL_CARE = "PERSONAL_CARE"
    INVESTMENT_SAVINGS = "INVESTMENT_SAVINGS"
    CHARITY_DONATIONS = "CHARITY_DONATIONS"
    LOANS_DEBT = "LOANS_DEBT"
    BETWEEN_ACCOUNTS = "BETWEEN_ACCOUNTS"
    MISCELLANEOUS_OTHER = "MISCELLANEOUS_OTHER"

    def __str__(self):
        return CATEGORY_EN_LOCAL_MAP[self]


CATEGORY_EN_LOCAL_MAP: dict[TransactionCategory, str] = {
    TransactionCategory.GROCERIES: "Groceries",
    TransactionCategory.DINING_ENTERTAINMENT: "Dining & Entertainment",
    TransactionCategory.UTILITIES: "Utilities like Electricity, Gas, Water, Internet, Phone",
    TransactionCategory.TAXES: "Taxes / Government Fees",
    TransactionCategory.SALARY: "Salary",
    TransactionCategory.HOUSING: "Housing",
    TransactionCategory.TRANSPORTATION: "Transportation",
    TransactionCategory.HEALTH_WELLNESS: "Health & Wellness",
    TransactionCategory.ONLINE_SHOPPING: "Online Shopping",
    TransactionCategory.TRAVEL: "Travel",
    TransactionCategory.EDUCATION_PROFESSIONAL: "Education & Professional Services",
    TransactionCategory.PERSONAL_CARE: "Personal Care",
    TransactionCategory.INVESTMENT_SAVINGS: "Investment & Savings",
    TransactionCategory.CHARITY_DONATIONS: "Charity & Donations",
    TransactionCategory.LOANS_DEBT: "Loans & Debt Payments",
    TransactionCategory.BETWEEN_ACCOUNTS: "Between Accounts",
    TransactionCategory.MISCELLANEOUS_OTHER: "Miscellaneous & Other"
}


class UserTransactionCategory(BaseModel):
    category_map: dict[str, TransactionCategory] = {}
    ignored_transactions_signatures: set[str] = set()
