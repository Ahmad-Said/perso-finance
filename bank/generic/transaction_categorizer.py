import json
import os
from typing import Optional

from bank.generic import tr_common_category
from bank.model.transaction import Transaction
from bank.model.transaction_category import TransactionCategory, UserTransactionCategory
from const.const_gl import ConstGl


class TransactionCategorizer:
    def __init__(self, user_category_file_map: str = None):
        if not user_category_file_map:
            user_category_file_map = os.path.join(ConstGl.PATH_TO_BANK_DATA, "user_category_map.json")
        self.user_category_file_map = user_category_file_map
        self.category_map: dict[str, TransactionCategory] = tr_common_category.COMMON_CATEGORY_MAP.copy()
        loaded_categories = self._load_category_user_file_map()
        self.category_map.update(loaded_categories.category_map)
        loaded_categories.category_map = self.category_map
        self.user_transaction_category = loaded_categories
        self._normalized_category_map = {}
        self.compute_normalized_map()

    def compute_normalized_map(self):
        # make all keys upper case
        normalized_map = {}
        for key, value in self.category_map.items():
            normalized_map[key.upper()] = value
        self._normalized_category_map = normalized_map

    def _load_category_user_file_map(self) -> UserTransactionCategory:
        if not self.user_category_file_map or not os.path.exists(self.user_category_file_map):
            return UserTransactionCategory()

        with open(self.user_category_file_map, 'r') as f:
            dic_map = json.load(f)

        # cast value to enum type
        return UserTransactionCategory(**dic_map)

    def save_category_user_file_map(self):
        parent_dir = os.path.dirname(self.user_category_file_map)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        with open(self.user_category_file_map, 'w', encoding='utf-8') as f:
            f.write(self.user_transaction_category.model_dump_json(indent=4))


    def search_category(self, transaction: Transaction) -> Optional[TransactionCategory]:
        if  transaction.get_signature() in self.user_transaction_category.ignored_transactions_signatures:
            return transaction.transaction_category
        description = transaction.description.upper()
        description_split_set = set(description.split())
        for key, value in self._normalized_category_map.items():
            key_split = key.split()
            # each part of key must be in description
            if all(part in description_split_set for part in key_split):
                return value
        return None

    def categorize(self, transaction: Transaction, ask_user: bool) -> Transaction:
        # Categorize transactions based on description
        category = self.search_category(transaction)
        if category:
            transaction.transaction_category = category
        elif ask_user:
            self.ask_user(transaction)
        return transaction

    def is_need_categorization(self, transaction: Transaction, minimum_amount_to_ask = 0) -> bool:
        return not self.search_category(transaction) and (transaction.expense_amount > minimum_amount_to_ask or transaction.income_amount > minimum_amount_to_ask)

    @staticmethod
    def _get_valid_index_or_empty(msg:str, minimum_value: int, max_value: int) -> Optional[int]:
        is_valid_index = False
        while not is_valid_index:
            try:
                idx_str = input(f"{msg} (Optional): ")
                if not idx_str.strip():
                    return None
                idx = int(idx_str)
                if minimum_value <= idx <= max_value:
                    is_valid_index = True
                    return idx
                else:
                    print(f"Invalid index. Please enter a value between {minimum_value} and {max_value}")
            except ValueError:
                print("Invalid index. Please enter a valid integer value.")

    def ask_user(self, transaction: Transaction):
        print("-" * 25 + "Transaction Categorization" + "-" * 25)
        print(f"\nTransaction description: {transaction.description}")
        print(f"Transaction expense: {transaction.expense_amount}")
        print(f"Transaction income: {transaction.income_amount}")
        print(f"Transaction date: {transaction.transaction_date}")
        print("Please select a category:")
        idx_to_category: dict[int, TransactionCategory] = {}
        category_to_idx: dict[TransactionCategory, int] = {}
        i = 1
        for _, category in TransactionCategory.__members__.items(): # type: TransactionCategory
            print(f"{i}: {category}")
            idx_to_category[i] = category
            category_to_idx[category] = i
            i += 1

        print(f"{i}: Ignore this transaction")
        idx = self._get_valid_index_or_empty("Choose category", 1, len(idx_to_category) + 1)
        if idx is None:
            idx = category_to_idx[TransactionCategory.MISCELLANEOUS_OTHER]
        if idx in idx_to_category:
            while True: # till valid pattern is entered
                key_description_name = input("Enter a key / pattern description name (Optional): ")
                if not key_description_name.strip():
                    key_description_name = transaction.description
                self.category_map[key_description_name] = idx_to_category[idx]
                self.compute_normalized_map()
                if self.search_category(transaction):
                    break
                del self.category_map[key_description_name]
                self.compute_normalized_map()
                print("Could not deduce the category from given pattern. Please try again.")
            transaction.transaction_category = idx_to_category[idx]
        else:
            self.user_transaction_category.ignored_transactions_signatures.add(transaction.get_signature())

        self.save_category_user_file_map()
        return transaction
