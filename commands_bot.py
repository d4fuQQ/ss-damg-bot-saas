from command_db import get_command_line, update_db
from constants import DEV_IDS
from discord_helpers import resolve_command_pieces, send_message


def get_commands_msg():

    msg = 'SS-DAMG Bot Scholar Commands\n'
    msg += '!commands'
    msg += '$qr'
    msg += '!rank'
    msg += '!payout'

    return msg


def get_commands_founders_msg():
    msg = 'SS-DAMG Bot Founder Commands\n'
    msg += '!commands founders'
    msg += '!rank top'
    msg += '!rank all'
    msg += '!pve'
    msg += '!earnings'
    msg += '!earnings product1'
    msg += '!earnings product2'
    msg += '!earnings product2_prep'
    msg += '!earnings product3'

    return msg


def get_command_permissions(command):
    command_line = get_command_line(command)

    if len(command_line.index) == 0:
        return []

    command_permissions = command_line.iloc[0]['permissioned_role_ids']

    return command_permissions


async def get_roles_for_command(command, channel, guild):
    current_permissions = get_command_permissions(command)
    current_perms_names = []

    for guild_role in guild.roles:
        if str(guild_role.id) in current_permissions:
            current_perms_names.append(guild_role.name)

    msg = 'The following roles have access to the {} command:'.format(command)
    for role in current_perms_names:
        msg += '\n'+role

    await send_message(msg, channel)


async def add_role_to_command(command, new_role, channel, guild):
    current_permissions = get_command_permissions(command)

    if new_role in current_permissions:
        return

    current_permissions.append(new_role)
    update_db(command, current_permissions)
    await get_roles_for_command(command, channel, guild)


async def remove_role_from_command(command, new_role, channel, guild):
    current_permissions = get_command_permissions(command)

    if new_role not in current_permissions:
        return

    current_permissions.remove(new_role)
    update_db(command, current_permissions)
    await get_roles_for_command(command, channel, guild)


def user_has_permission(user, command):
    if user is None:
        return False

    #current_permissions = get_command_permissions(command)

    #user_roles = [str(role.id) for role in user.roles]

    arr = [490989299911884800, 574690954380836874]
    if user.id in arr:
        return True

    print('User {} does not have permission for command {}'.format(user.name, command))

    return False


async def run_command_bot(user, channel, guild, msg_pieces):
    if user.id not in DEV_IDS:
        return

    if len(msg_pieces) < 2:
        return
    print('here')

    if msg_pieces[1] == 'add_role':
        print('Adding role....')
        msg_pieces = msg_pieces[2:]
        command_piece_end = resolve_command_pieces(msg_pieces)
        command = (' '.join(msg_pieces[:command_piece_end + 1])).replace('"', '')
        role = msg_pieces[command_piece_end + 1]
        await add_role_to_command(command, role, channel, guild)

    elif msg_pieces[1] == 'remove_role':
        msg_pieces = msg_pieces[2:]
        command_piece_end = resolve_command_pieces(msg_pieces)
        command = (' '.join(msg_pieces[:command_piece_end + 1])).replace('"', '')
        role = msg_pieces[command_piece_end + 1]
        await remove_role_from_command(command, role, channel, guild)

    elif msg_pieces[1] == 'view_roles':
        msg_pieces = msg_pieces[2:]
        command_piece_end = resolve_command_pieces(msg_pieces)
        command = (' '.join(msg_pieces[:command_piece_end + 1])).replace('"', '')

        await get_roles_for_command(command, channel, guild)
