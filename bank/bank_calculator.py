import os
from decimal import Decimal

import pandas as pd
from tqdm import tqdm

from bank.bnp.bnp_hello_statement_extractor import BNPHelloStatementExtractor
from bank.bnp.bnp_statement_extractor import BNPStatementExtractor
from bank.generic.bank_statement_extractor import BankStatementExtractor
from bank.generic.transaction_categorizer import TransactionCategorizer
from bank.model.transaction import BankStatement
from bank.revolut.revolut_statement_extractor import RevolutStatementExtractor
from bank.sg.sg_statement_extractor import SGStatementExtractor
from const.const_gl import ConstGl
from util.result_file_cache import ResultFileCache


def extract_transactions(directory: str,
                         extractor: BankStatementExtractor,
                         result_cache: ResultFileCache) -> list:
    if not os.path.exists(directory):
        return []
    doc_statements = os.listdir(directory)
    all_transactions = []
    for doc_statement in tqdm(doc_statements, desc="Processing statements from " + directory):
        doc_path = os.path.join(directory, doc_statement)
        bank_statement = result_cache.get_or_process_document(doc_path, extractor.extract_and_validate)
        all_transactions.extend(bank_statement.transactions)
    return all_transactions

def main():
    print("main")
    result_hasher = ResultFileCache()
    all_transactions = []
    banks_path_tuples = [
        (ConstGl.PATH_TO_BANK_DATA_BNP, BNPStatementExtractor()),
        (ConstGl.PATH_TO_BANK_DATA_HELLO_BANK, BNPHelloStatementExtractor()),
        (ConstGl.PATH_TO_BANK_DATA_REVOLUT, RevolutStatementExtractor()),
        (ConstGl.PATH_TO_BANK_DATA_SG, SGStatementExtractor()),
    ]
    transaction_categorizer = TransactionCategorizer()
    for bank_path, extractor in banks_path_tuples:
        all_transactions.extend(extract_transactions(bank_path, extractor, result_hasher))


    for transaction in tqdm(all_transactions, desc="Categorizing transactions"):
        if transaction_categorizer.is_need_categorization(transaction, 5000):
            transaction_categorizer.categorize(transaction, True)
        else:
            transaction_categorizer.categorize(transaction, False)


    xlsx_file = ConstGl.TEMP_DIR + '/all_transactions.xlsx'
    all_transactions_dict = [transaction.model_dump() for transaction in all_transactions]
    df = pd.DataFrame(all_transactions_dict)
    # Convert Decimal columns to float
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

    df.to_excel(xlsx_file, index=False)

if __name__ == '__main__':
    main()