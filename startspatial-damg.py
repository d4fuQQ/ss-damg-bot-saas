import argparse

from commands_bot import run_command_bot
from qr_code_bot import *
from datetime import datetime

from constants import SCHOLARS_CHAT_CHANNEL, MASTERS_CHAT_CHANNEL, DISCORD_BOT_TOKEN
from pve_slp_api import get_daily_pve_summary
from slp_bot import get_individual_rank_msg, get_top_rank_msg, get_all_rank_msg
from earnings_bot import get_product_earnings_msg
from payout_bot import run_update_payout, payout_pull, payout_request_scholars
from axie_bot import get_axie_info

now = datetime.now()
client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg_pieces = message.content.split()
    if len(msg_pieces) == 0:
        return

    if msg_pieces[0] == "$qr":
        await qr_bot(message, msg_pieces)
        return

    elif msg_pieces[0] == '!rank':
        if len(msg_pieces) > 1 and msg_pieces[1] == 'top':
            await get_top_rank_msg(message.author, message.channel)
            return

        elif len(msg_pieces) > 1 and msg_pieces[1] == 'all':
            await get_all_rank_msg(message.author, message.channel)
            return

        else:
            await get_individual_rank_msg(message.author, message.channel)
            return

    elif msg_pieces[0] == '!pve':
        await get_daily_pve_summary(message.author, message.channel)
        return

    elif msg_pieces[0] == '!earnings':
        if len(msg_pieces) == 1:
            await get_product_earnings_msg(message.author, message.channel, 'ss-damg')
            return

        elif len(msg_pieces) == 2 and (msg_pieces[1] == 'product1' or 'product2' or 'product2_prep'
                                       or 'product3' or 'mike'):
            await get_product_earnings_msg(message.author, message.channel, msg_pieces[1])
            return

    elif msg_pieces[0] == '!payout' and len(msg_pieces) == 2:
        if msg_pieces[1] == 'request':
            await payout_request_scholars(message.author, message.channel)
            return

        elif msg_pieces[1] == 'pull':
            await payout_pull(message.author, message.channel)
            return

        else:
            await run_update_payout(message.author, message.channel, msg_pieces[1])
            return

    elif msg_pieces[0] == '!commands':
        await run_command_bot(message.author, message.channel, message.guild, msg_pieces)
        return


@client.event
async def on_ready():
    print('\nWe are logged in as {0.user}'.format(client))

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--top_rank', required=False, default=None, dest='top_rank', action='store_true')
    parser.add_argument('-p', '--pve_slp', required=False, default=None, dest='pve_slp', action='store_true')
    parsed_args = parser.parse_args()

    if parsed_args.top_rank:
        try:
            await get_top_rank_msg(user=None, channel=client.get_channel(SCHOLARS_CHAT_CHANNEL), override=True)
            await client.close()
            return
        except Exception as e:
            print('Exception: {}'.format(e))
            await client.close()
            return

    elif parsed_args.pve_slp:
        try:
            await get_daily_pve_summary(user=None, channel=client.get_channel(MASTERS_CHAT_CHANNEL), override=True)
            await client.close()
            return
        except Exception as e:
            print('Exception: {}'.format(e))
            await client.close()
            return


client.run(DISCORD_BOT_TOKEN)
