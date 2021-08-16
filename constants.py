import os

ENCRYPTED_SCHOLAR_CSV = 'scholar_store_encrypted.csv'

LUNACIAROVER_ENDPOINT = 'https://api.lunaciarover.com/stats/{}'
PVE_SLP_ENDPOINT = 'https://axieboard.vercel.app/api/game/pve?address={}'
GRAPHQL_ENDPOINT = 'https://axieinfinity.com/graphql-server-v2/graphql'
AXIE_ENDPOINT = 'https://axie-proxy.secret-shop.buzz/_axiesPlease/{}'
AXIE_IMAGE_ENDPONT = 'https://storage.googleapis.com/assets.axieinfinity.com/axies/{}/axie/axie-full-transparent.png'
CRYPTO_API_ENDPOINT = 'https://min-api.cryptocompare.com/data/price?fsym='

WEB3_FREE_GAS_RPC = 'https://proxy.roninchain.com/free-gas-rpc'
WEB3_RONIN_RPC = 'https://api.roninchain.com/rpc'
SLP_CONTRACT_ADDR = "0x364cbb653ca0eba8fe2bf0a505529627802c31a5"

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
MAX_RETRIES = 3
SLP_TABLE_NAME = 'slp_table'
AXIE_TABLE_NAME = 'axie_table'
PAYOUT_TABLE_NAME = 'payout_table'
TIMESTAMP_FORMAT = "%Y-%m-%d %I:%M:%S"

DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
CRYPTO_API_TOKEN = os.getenv('CRYPTO_API_TOKEN')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
ACADEMY_PAYOUT_ADDRESS = os.getenv('ACADEMY_PAYOUT_ADDRESS')

SCHOLARS_CHAT_CHANNEL = ''
MASTERS_CHAT_CHANNEL = ''
FOUNDERS_BOT_CHANNEL = ''

MIN_DAYS_FOR_INCLUSION = 5.0

# Founders/Investors
DEV_IDS = [490989299911884800, 514672694092890112, 399749457727586304, 574690954380836874]
# Coaches/Mods
MASTER_IDS = [836432162060107816, 857922053129895957, 838395965647487016]

MAX_DISCORD_MESSAGE_LENGTH = 2000

CHOOSE_NTH_AXIE_FOR_SHARE_PRICE = 5

SCHOLARSHIP_SHARE = .6
