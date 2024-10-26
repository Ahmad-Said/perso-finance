import os
from decimal import Decimal

import pandas as pd

from bank.bnp.bnp_statement_extractor import BNPStatementExtractor
from const.const_gl import ConstGl


def main():
    print("main")
    bnp_extractor = BNPStatementExtractor()
    pdf_statements = os.listdir(ConstGl.PATH_TO_BANK_DATA_BNP)
    all_transactions = []
    for pdf_statement in pdf_statements:
        pdf_path = os.path.join(ConstGl.PATH_TO_BANK_DATA_BNP, pdf_statement)
        bank_statement = bnp_extractor.extract_statement(pdf_path)
        bank_statement.validate_statement()
        all_transactions.extend(bank_statement.transactions)
        print(bank_statement)

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