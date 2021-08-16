import argparse
import uuid
import os
import discord
import qrcode

from encryption import return_scholar_dict
from qr_code_bot import *
from datetime import datetime

from constants import SCHOLARS_CHAT_CHANNEL, DEV_IDS, MASTER_IDS, MASTERS_CHAT_CHANNEL, DISCORD_BOT_TOKEN, \
    FOUNDERS_BOT_CHANNEL
from pve_slp_api import get_daily_pve_summary
from slp_bot import get_individual_rank_msg, get_top_rank_msg, get_all_rank_msg
from earnings_bot import get_product_earnings_msg
from payout_bot import run_update_payout, payout_pull, payout_request_scholars

now = datetime.now()
client = discord.Client()


def log(msg):
    print(msg)


@client.event
async def on_ready():
    print('\nWe are logged in as {0.user}'.format(client))

    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--top_rank', required=False, default=None, dest='top_rank', action='store_true')
    parser.add_argument('-p', '--pve_slp', required=False, default=None, dest='pve_slp', action='store_true')

    parsed_args = parser.parse_args()

    if parsed_args.top_rank:
        try:
            message_to_send = get_top_rank_msg()

            if not message_to_send:
                print('Not enough qualified scholars to make a leaderboard')
            else:
                print('\n{}\n'.format(message_to_send))
                channel = client.get_channel(SCHOLARS_CHAT_CHANNEL)
                embed = discord.Embed(description=message_to_send)
                await channel.send(embed)
            await client.close()
            return
        except Exception as e:
            print('Exception: {}'.format(e))
            await client.close()
            return

    elif parsed_args.pve_slp:
        try:
            channel = client.get_channel(MASTERS_CHAT_CHANNEL)

            msg = get_daily_pve_summary()
            print(msg)
            embed = discord.Embed(description=msg)
            await channel.send(embed=embed)
            await client.close()
            return
        except Exception as e:
            print('Exception: {}'.format(e))
            await client.close()
            return


@client.event
# Listen for an incoming message
async def on_message(message):
    if message.author == client.user:
        return
    scholar_dict = return_scholar_dict()
    if message.content == "$qr":
        if str(message.author.id) in scholar_dict:
            scholar_info = scholar_dict[str(message.author.id)]
            account_private_key = scholar_info[2]
            account_address = scholar_info[1]

            # Get a message from AxieInfinity
            raw_message = get_raw_message()
            # Sign that message with account_private_key
            signed_message = get_sign_message(raw_message, account_private_key)
            # Get an access_token by submitting the signature to AxieInfinity
            access_token = submit_signature(signed_message, raw_message, account_address)

            if not access_token:
                msg = "Hi <@{}>, The QR bot is having trouble right now. Feel free to try again in a few" \
                      " seconds. If that doesn't work, we suggest logging in with your username and " \
                      "password.".format(message.author.id)

                print("\nSent to {}:".format(message.author.name))
                print("\n{}\n".format(msg))
                embed = discord.Embed(description=msg)
                await message.author.send(embed)
                return

            # Create a QrCode with that access_token
            qr_code_path = f"QRCode_{message.author.id}_{str(uuid.uuid4())[0:8]}.png"
            qrcode.make(access_token).save(qr_code_path)
            # Send the QrCode the the user who asked for
            await message.author.send(
                "------------------------------------------------\n\n\nHello " + message.author.name + "\nHere is your new QR Code to login : ")
            await message.author.send(file=discord.File(qr_code_path))
            os.remove(qr_code_path)
            print("This user received his QR Code : " + message.author.name)
            print("Discord ID : " + str(message.author.id))
            return
        else:
            print("This user didn't receive a QR Code : " + message.author.name)
            print("Discord ID : " + str(message.author.id))
            return
    msg_pieces = message.content.split()

    if len(msg_pieces) == 0:
        return

    if msg_pieces[0] == '!rank':
        if len(msg_pieces) > 1:
            if msg_pieces[1] == 'top':
                if message.author.id not in DEV_IDS:
                    print('User {} with id {} does not have access to !rank top'.format(message.author.name,
                                                                                        message.author.id))
                    return

                message_to_send = get_top_rank_msg()
                print('\n{}\n'.format(message_to_send))
                embed = discord.Embed(description=message_to_send)
                await message.channel.send(embed=embed)
                return
            elif msg_pieces[1] == 'all':
                if message.author.id not in DEV_IDS:
                    print('User {} with id {} does not have access to !rank all'.format(message.author.name,
                                                                                        message.author.id))
                    return

                message_to_send = get_all_rank_msg()
                embed = discord.Embed(description=message_to_send)
                await message.channel.send(embed=embed)

            return

        if str(message.author.id) not in scholar_dict:
            msg = 'Discord id {} not found in dict for user {}'.format(message.author.id, message.author.name)
            print(msg)
            channel = client.get_channel(FOUNDERS_BOT_CHANNEL)
            embed = discord.Embed(description=msg)
            channel.send(embed)
        else:
            scholar_info = scholar_dict[str(message.author.id)]
            name = scholar_info[0]
            ronin_address = scholar_info[1]

            message_to_send = get_individual_rank_msg(ronin_address)
            embed = discord.Embed(description=message_to_send)

            print('\n{}\n'.format(message_to_send))

            if not message_to_send:
                print("Failed to retrieve info for {} at address {}".format(name, ronin_address))

            try:
                await message.author.send(embed=embed)
            except discord.Forbidden:
                await message.channel.send(
                    'Hi, <@{}>. Please enable DMs as described in https://discord.com/channels/826075132346499094/838121815653220382/869038272612036649'
                        .format(message.author.id))
            return

    elif msg_pieces[0] == '!pve':
        if message.author.id not in MASTER_IDS:
            print('User {} with id {} does not have access to !pve'.format(message.author.name, message.author.id))
            return

        msg = get_daily_pve_summary()
        print(msg)
        embed = discord.Embed(description=msg)
        await message.channel.send(embed=embed)
        return

    elif msg_pieces[0] == '!earnings':
        if message.author.id not in DEV_IDS:
            print('User {} with id {} does not have access to !earnings'.format(message.author.name, message.author.id))
            return

        if len(msg_pieces) == 1:
            msg_title, msg = get_product_earnings_msg('ss-damg')

        elif len(msg_pieces) == 2:
            if msg_pieces[1] == 'product1' or 'product2' or 'product2_prep' or 'product3' or 'mike':
                msg_title, msg = get_product_earnings_msg(msg_pieces[1])
            else:
                print('Not a valid product.')
                return

        else:
            print('Not a valid product.')
            return

        print(msg)
        embed = discord.Embed(title=msg_title, description=msg)
        await message.channel.send(embed=embed)
        return

    elif msg_pieces[0] == '!payout':
        if message.author.id in DEV_IDS:
            if msg_pieces[1] == 'request':
                msg = payout_request_scholars()
                embed = discord.Embed(description=msg)
                await message.channel.send(embed=embed)
            else:
                print(
                    'User {} with id {} does not have access to !payout'.format(message.author.name, message.author.id))
            return

        if len(msg_pieces) == 2:
            if msg_pieces[1].startswith('ronin:') or msg_pieces[1].startswith('0x'):
                print('User {} input valid address'.format(message.author.id))
                run_update_payout(message.author.id, msg_pieces[1])
                msg = 'Hi, <@{}>. Your payout address was successfully updated!' \
                    .format(message.author.id)
                embed = discord.Embed(description=msg)
                await message.channel.send(embed=embed)

            elif msg_pieces[1] == 'pull':
                msg = payout_pull(message.author.id)
                embed = discord.Embed(description=msg)
                await message.channel.send(embed=embed)

            else:
                print('User {} with input address {} was not valid'.format(message.author.name, msg_pieces[1]))
                msg = 'Hi, <@{}>. Input valid ronin or slp payout address as !payout your_address_here' \
                    .format(message.author.id)
                embed = discord.Embed(description=msg)
                await message.channel.send(embed=embed)
                return

        else:
            print('User {} needs to input ronin address with command'.format(message.author.name))
            msg = 'Hi, <@{}>. Input new command !payout your_address_here'.format(message.author.id)
            embed = discord.Embed(description=msg)
            await message.channel.send(embed=embed)
            return

    return


client.run(DISCORD_BOT_TOKEN)
