import os

ENCRYPTED_SCHOLAR_CSV = 'scholar_store_encrypted.csv'

LUNACIAROVER_ENDPOINT = 'https://game-api.axie.technology/api/v1/{}'
PVE_SLP_ENDPOINT = 'https://axieboard.vercel.app/api/game/pve?address={}'
GRAPHQL_ENDPOINT = 'https://axieinfinity.com/graphql-server-v2/graphql'
AXIE_ENDPOINT = 'https://axie-proxy.secret-shop.buzz/_axiesPlease/{}'
AXIE_IMAGE_ENDPONT = 'https://storage.googleapis.com/assets.axieinfinity.com/axies/{}/axie/axie-full-transparent.png'
CRYPTO_API_ENDPOINT = 'https://min-api.cryptocompare.com/data/price?fsym='

WEB3_FREE_GAS_RPC = 'https://proxy.roninchain.com/free-gas-rpc'
WEB3_RONIN_RPC = 'https://api.roninchain.com/rpc'
SLP_CONTRACT_ADDR = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
MAX_RETRIES = 3
SLP_TABLE_NAME = 'slp_table'
AXIE_TABLE_NAME = 'axie_table'
PAYOUT_TABLE_NAME = 'payout_table'
COMMAND_TABLE_NAME = 'command_table'
TIMESTAMP_FORMAT = "%Y-%m-%d %I:%M:%S"

DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
CRYPTO_API_TOKEN = os.getenv('CRYPTO_API_TOKEN')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
ACADEMY_PAYOUT_ADDRESS = os.getenv('ACADEMY_PAYOUT_ADDRESS')

SCHOLARS_CHAT_CHANNEL = 880522613674360842
MASTERS_CHAT_CHANNEL = 865993699490398208
FOUNDERS_BOT_CHANNEL = 876627977960583290

MIN_DAYS_FOR_INCLUSION = 3

DEV_IDS = [490989299911884800, 574690954380836874]
SCHOLARS_TO_EXCLUDE_FROM_TOP_RANK = []
DEV_RONIN_ADDRESSES = []

MAX_DISCORD_EMBED_MESSAGE_LENGTH = 4096

PLAYERS_IN_TOP_RANK_COMMAND = 10

SCHOLARSHIP_SHARE = .7
