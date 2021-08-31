import datetime

from commands_bot import user_has_permission
from discord_helpers import send_message
from encryption import return_scholar_dict
from share_price_api import get_crypto_price
from slp_db import get_entire_db


# Given product ID, return list of addresses assoc. with product
def get_product_scholars(product):
    product_addresses = []

    scholar_dict = return_scholar_dict()

    if product == 'ss-damg':
        for info in scholar_dict.values():
            if info[3] != 'mike':
                product_addresses.append(info[1])

    if product == 'product1' or 'product2' or 'product2_prep' or 'product3' or 'product4' or 'mike':
        for info in scholar_dict.values():
            if info[3] == product:
                product_addresses.append(info[1])

    return product_addresses


# Given product ID, return unclaimed slp earnings assoc. with product
async def get_product_earnings_msg(user, channel, product):
    if not user_has_permission(user, "!earnings"):
        return

    df = get_entire_db()
    product_addresses = get_product_scholars(product)

    df_product = df[df['address'].isin(product_addresses)]
    product_earnings = df_product['unclaimed_slp'].sum()

    slp_price = get_crypto_price('SLP')
    product_earnings_usd = round(product_earnings * slp_price, 2)

    msg_title = 'Monthly earnings as of {}\n'.format(datetime.datetime.today().strftime('%Y-%m-%d'))
    msg = 'Total earnings for {}: {:,.2f} SLP\n'.format(product, int(product_earnings))
    msg += 'Equivalent to ${:,.2f}'.format(product_earnings_usd)

    await send_message(msg, channel, title=msg_title)
