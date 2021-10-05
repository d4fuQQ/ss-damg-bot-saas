# TODO: Make this check for the whole thing being accurate
def is_valid_ronin_address(address):
    return address.startswith("ronin:")


def get_axie_url(id):
    return 'https://marketplace.axieinfinity.com/axie/'+str(id)
