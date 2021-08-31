import math

import discord

from constants import MAX_DISCORD_EMBED_MESSAGE_LENGTH


def get_messages_under_max_size(message):
    if len(message) <= MAX_DISCORD_EMBED_MESSAGE_LENGTH:
        return [message]

    num_newlines = message.count('\n')

    if num_newlines == 0:
        message_midpoint = len(message) / 2
        return [message[:message_midpoint], message[message_midpoint:]]

    middle_newline = math.ceil(num_newlines / 2)

    lines = message.split('\n')

    return ['\n'.join(lines[:middle_newline]), '\n'.join(lines[middle_newline:])]


async def send_message(message_to_send: str, to, received_message=None, title=None):
    print('\n{}\n'.format(message_to_send))
    messages = get_messages_under_max_size(message_to_send)

    for index in range(len(messages)):
        if title is not None and index == 0:
            embed = discord.Embed(description=messages[index], title=title)
        else:
            embed = discord.Embed(description=messages[index])
        try:
            await to.send(embed=embed)
        except discord.Forbidden:
            if received_message is not None and index == 0:
                await received_message.channel.send('Hi, <@{}>. Please enable discord Direct Messages in settings.'
                                                    .format(received_message.author.id))


def resolve_command_pieces(pieces):
    if len(pieces) == 0:
        raise Exception('Command required')

    if pieces[0].startswith('"'):
        for piece_number in range(len(pieces)):
            if pieces[piece_number].endswith('"'):
                return piece_number
        raise Exception('Ending quotation not found.')

    return 0
