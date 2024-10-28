import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pdfplumber

from bank.bnp.bnp_statement_extractor import BNPStatementExtractor
from bank.generic.bank_statement_extractor import BankStatementExtractor
from bank.model.transaction import BankStatement, Transaction


class BNPHelloStatementExtractor(BNPStatementExtractor):
    BANK_NOMINATION = "Hello Bank"