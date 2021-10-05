from cryptography.fernet import Fernet

import argparse

from constants import ENCRYPTED_SCHOLAR_CSV, ENCRYPTION_KEY


def return_scholar_dict():
    fern = Fernet(ENCRYPTION_KEY)

    with open(ENCRYPTED_SCHOLAR_CSV, 'rb') as enc_f:
        enc = enc_f.read()

    dec = fern.decrypt(enc)
    decrypted_decoded = str(dec.decode('utf-8'))

    scholars_dict = {}

    for line in decrypted_decoded.split('\n'):
        line = line.strip().split(',')

        if len(line) < 5:
            continue

        discord_id = line[0].strip()
        discord_name = line[1].strip()
        ronin_wallet_address = line[2].strip()
        ronin_private_key = line[3].strip()
        product = line[4].strip()
        percent = line[5].strip()

        if len(discord_id) == 0 or len(discord_name) == 0 or len(ronin_wallet_address) == 0 \
                or len(ronin_private_key) == 0:
            continue

        try:
            int(discord_id)
        except:
            continue

        scholars_dict[discord_id] = [discord_name, ronin_wallet_address, ronin_private_key, product, percent]

    return scholars_dict


def get_address_to_discord_id_dict():
    address_to_discord_id = {}

    for discord_id, info in return_scholar_dict().items():
        address_to_discord_id[info[1]] = discord_id

    return address_to_discord_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', required=False, default=None, type=str)
    parser.add_argument('-o', '--output_file', required=False, default=None, type=str)
    parser.add_argument('-m', '--mode', required=True, default=None, type=str)
    parser.add_argument('-k', '--encryption_key', required=False, default=None, type=str)
    parsed_args = parser.parse_args()

    if parsed_args.mode == 'encrypt':
        fernet = Fernet(parsed_args.encryption_key)
        with open(parsed_args.input_file, 'rb') as decrypted_file:
            original = decrypted_file.read()
        encrypted = fernet.encrypt(original)
        with open(parsed_args.output_file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

    elif parsed_args.mode == 'decrypt':
        fernet = Fernet(parsed_args.encryption_key)
        with open(parsed_args.input_file, 'rb') as encrypted_file:
            encrypted = encrypted_file.read()
        decrypted = fernet.decrypt(encrypted)
        with open(parsed_args.output_file, 'wb') as decrypted_file:
            decrypted_file.write(decrypted)

    elif parsed_args.mode == 'genkey':
        key = Fernet.generate_key()
        print(key)

    else:
        raise Exception('Mode must be either encrypt, decrypt, or genkey')
