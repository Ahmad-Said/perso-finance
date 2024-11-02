import datetime
import logging
from decimal import Decimal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from bank.ai import model_provider
from bank.model.transaction import Transaction
from bank.model.transaction_category import TransactionCategory


class CategoryPredictor:
    logger = logging.getLogger("CategoryPredictor")
    def __init__(self):
        self.system_msg: SystemMessage = self._get_system_prompt()
        self.model: BaseChatModel = model_provider.get_model()

    def set_log_level(self, level: str):
        self.logger.setLevel(level)

    def _get_system_prompt(self, ) -> SystemMessage:
        system_message = """You are a smart assistant that help user to categorize his transaction to one of these categories below.
        Output should the key of the category only.
        """

        categories = ""
        for category in TransactionCategory:
            categories += f"{category.name}: {category}\n"
        system_message += categories
        return SystemMessage(system_message)

    def serialize_transaction(self, transaction: Transaction) -> str:
        if transaction.expense_amount > 0:
            user_message = "paid for " + transaction.description + " " + str(transaction.expense_amount) + " euros"
        else:
            user_message = "received " + str(transaction.income_amount) + " euros" + " from " + transaction.description
        return user_message

    def predict_transaction_category(self, transaction: Transaction) -> TransactionCategory:
        transaction_str = self.serialize_transaction(transaction)
        messages = [
            self.system_msg,
            HumanMessage(transaction_str)
        ]
        ai_response = self.model.invoke(messages)
        self.logger.debug(f"AI response: {ai_response}")
        try:
            return TransactionCategory[ai_response.content.upper()]
        except KeyError:
            self.logger.error(f"Invalid category: {ai_response.content}")
            return TransactionCategory.MISCELLANEOUS_OTHER


def main():
    # Set up basic logging configuration
    logging.basicConfig(level=logging.INFO)

    transaction = Transaction(
        bank_nomination="NA",
        transaction_date=datetime.datetime.now(),
        description="Netflix",
        expense_amount=Decimal(10),
        income_amount=Decimal(0),
        proof_document="",
    )
    try:
        predictor = CategoryPredictor()
        predictor.set_log_level("DEBUG")
    except Exception as e:
        print(f"Error: {e}")
        return
    print("Transaction prediction: ")
    category = predictor.predict_transaction_category(transaction)
    transaction.transaction_category = category
    print(f"Predicted category: {category}")


if __name__ == '__main__':
    main()
