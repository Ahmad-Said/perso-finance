from bank.model.transaction import BankStatement


class BankStatementExtractor:
    BANK_NOMINATION = "Generic"
    def extract_statement(self, statement_doc: str) -> BankStatement:
        raise NotImplementedError

    def extract_and_validate(self, statement_doc: str) -> BankStatement:
        bank_statement = self.extract_statement(statement_doc)
        bank_statement.validate_statement()
        return bank_statement