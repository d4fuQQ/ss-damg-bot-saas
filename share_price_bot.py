from constants import CHOOSE_NTH_AXIE_FOR_SHARE_PRICE
from share_price_api import get_crypto_price


def get_current_share_price_2():
    slp_price = get_crypto_price('SLP')
    axs_price = get_crypto_price('AXS')

    product2_price = (((900*slp_price) + (2*axs_price)) * 3) + 25

    return f"P2: ${product2_price}"


