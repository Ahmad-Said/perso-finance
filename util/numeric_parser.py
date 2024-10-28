from decimal import Decimal, InvalidOperation


def is_decimal(s) -> tuple[bool, Decimal]:
    # example of input: "1 234,56" or "1.234,56"
    if not s:
        return False, Decimal(0)
    s = s.replace('.', ' ') \
        .replace(',', '.') \
        .replace(' ', '')  \
        .replace('*', '')
    try:
        value = Decimal(s)
        return True, value
    except InvalidOperation:
        return False, Decimal(0)
