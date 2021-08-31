# TODO: Make this check for the whole thing being accurate
def is_valid_ronin_address(address):
    return address.startswith("0x") or address.startswith("ronin:")