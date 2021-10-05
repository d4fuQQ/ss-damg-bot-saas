import math
import os
import sys
import time
from collections import namedtuple
from datetime import datetime

from web3 import Web3

import slp_utils
from constants import ACADEMY_PAYOUT_ADDRESS, WEB3_FREE_GAS_RPC
from encryption import return_scholar_dict
from helpers import is_valid_ronin_address
from payout_db import get_scholar_payout_address

RONIN_ADDRESS_PREFIX = "ronin:"

# Data types
Transaction = namedtuple("Transaction", "from_address to_address amount")
Payout = namedtuple("Payout", "name private_key nonce slp_balance scholar_transaction academy_transaction")
SlpClaim = namedtuple("SlpClaim", "name address private_key slp_claimed_balance slp_unclaimed_balance state")


def parse_ronin_address(address):
    if address.startswith(RONIN_ADDRESS_PREFIX):
        return Web3.toChecksumAddress(address.replace(RONIN_ADDRESS_PREFIX, "0x"))

    elif address.startswith("0x"):
        return Web3.toChecksumAddress(address)

    raise Exception("Address {} does not start with 0x or ronin:".format(address))


def get_private_key(key):
    if not key.startswith("0x"):
        return "0x" + key
    return key


def format_ronin_address(address):
    return address.replace("0x", RONIN_ADDRESS_PREFIX)


def check_all_valid_and_no_duplicates():
    scholar_dict = return_scholar_dict()

    existing_addresses = set()
    errored = False

    for discord_id, info in scholar_dict.items():
        name = info[0]
        address = info[1]
        if not (is_valid_ronin_address(address) or address.startswith('0x')):
            log('Found invalid address for user {}: {}'.format(name, address), error=True)
            errored = True
        if address in existing_addresses:
            log('Address {} for user {} is already assigned to someone else.'.format(address, name), error=True)
            errored = True
        else:
            existing_addresses.add(address)

    return not errored


def log(message="", end="\n", error=False):
    print(message, end=end, flush=True)
    sys.stdout = log_file
    print(message, end=end)  # print to log file
    if error:
        sys.stdout = error_file
        print(message, end=end)
    sys.stdout = original_stdout  # reset to original stdout
    log_file.flush()


def wait(seconds):
    for i in range(0, seconds):
        time.sleep(1)
        log(".", end="")
    log()


if not check_all_valid_and_no_duplicates():
    raise Exception('Issues were found in your scholar store. Please address them before trying again.')

web3 = Web3(Web3.HTTPProvider(WEB3_FREE_GAS_RPC))

now_dt = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
log_path = f"logs/logs-{now_dt}.txt".replace(':', "_")
error_path = f"logs/logs-{now_dt}_error.txt".replace(':', "_")

if not os.path.exists(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path))
log_file = open(log_path, "a", encoding="utf-8")
error_file = open(error_path, "a", encoding="utf-8")
original_stdout = sys.stdout

log(f"*** Welcome to the SLP Payout program *** ({datetime.now()})")

# Load accounts data.
if len(sys.argv) != 2:
    log("Please specify the path to the csv config file as parameter.")
    exit()

nonces = {}

with open(sys.argv[1]) as f:
    accounts = return_scholar_dict()

academy_payout_address = parse_ronin_address(ACADEMY_PAYOUT_ADDRESS)

# Check for unclaimed SLP
log("Checking for unclaimed SLP")
slp_claims = []
product_totals = {}
num_accounts = len(accounts)
index = 0

for _, scholar_info in accounts.items():
    index += 1

    scholar_name = scholar_info[0]
    account_address = parse_ronin_address(scholar_info[1])
    product = scholar_info[3]
    scholar_payout_address = get_scholar_payout_address(account_address)

    if scholar_payout_address is None:
        log('Scholar {} with address {} has no payout address entered, skipping...'
            .format(scholar_name, account_address))
        continue

    try:
        slp_unclaimed_balance = slp_utils.get_unclaimed_slp(account_address)
        nonce = nonces[account_address] = web3.eth.get_transaction_count(account_address)
    except Exception as e:
        log('(Failed to get unclaimed slp for {}, skipping. Exception: {}'.format(scholar_name, e), error=True)
        continue

    log("({}/{}) Account {} (nonce: {}) has {} unclaimed SLP.".format(index, num_accounts, scholar_name,
                                                                      nonce, slp_unclaimed_balance))

    if slp_unclaimed_balance > 0:
        slp_claims.append(SlpClaim(
            name=scholar_name,
            address=account_address,
            private_key=get_private_key(scholar_info[2]),
            slp_claimed_balance=slp_utils.get_claimed_slp(account_address),
            slp_unclaimed_balance=slp_unclaimed_balance,
            state={"signature": None}))

        if product not in product_totals:
            product_totals[product] = 0
        product_totals[product] += slp_unclaimed_balance

log()
log()

for product, total in product_totals.items():
    log('{} SLP available to claim for product {}'.format(total, product))

log("Would you like to claim SLP? [y]/N", end=" ")

if input() == "y":
    try:
        for slp_claim in slp_claims:
            log(f"   Claiming {slp_claim.slp_unclaimed_balance} SLP for '{slp_claim.name}'...")
            try:
                slp_utils.execute_slp_claim(slp_claim, nonces)
            except Exception as e:
                time.sleep(0.250)
                log("FAILED to claim for {}. Exception: {}".format(slp_claim.name, e))
                continue
            log("DONE")
        log("Waiting 30 seconds", end="")
        wait(30)

        completed_claims = []
        for slp_claim in slp_claims:
            if slp_claim.state["signature"] is not None:
                print(account_address)
                slp_total_balance = slp_utils.get_claimed_slp(account_address)
                print(slp_total_balance)
                print(slp_claim.slp_claimed_balance)
                print(slp_claim.slp_unclaimed_balance)
                if slp_total_balance >= slp_claim.slp_claimed_balance + slp_claim.slp_unclaimed_balance:
                    completed_claims.append(slp_claim)

        for completed_claim in completed_claims:
            slp_claims.remove(completed_claim)

        if len(slp_claims) > 0:
            log("The following claims didn't complete successfully:")
            for slp_claim in slp_claims:
                log(f"  - Account '{slp_claim.name}' has {slp_claim.slp_unclaimed_balance} unclaimed SLP.")
        else:
            log("All claims completed successfully!")
    except Exception as e:
        log(str(type(e)))
        log('(Scholar: ' + slp_claim.name + '): ' + str(e), error=True)

log()
log("Please review the payouts for each scholar:")

# Generate transactions.
payouts = []

curr_index = 0
for _, scholar_info in accounts.items():
    curr_index += 1
    scholar_name = scholar_info[0]
    account_address = parse_ronin_address(scholar_info[1])

    scholar_payout_address = get_scholar_payout_address(account_address)

    if scholar_payout_address is None:
        log('({}/{}) Scholar {} with address {} has no payout address entered, skipping...'
            .format(curr_index, num_accounts, scholar_name, account_address))
        continue
    else:
        try:
            scholar_payout_address = parse_ronin_address(get_scholar_payout_address(account_address))
        except ValueError as e:
            log('({}/{}) Scholar {} payout address is invalid. Exception: {}'.format(curr_index, num_accounts,
                                                                                     scholar_name, e),
                error=True)
            continue

    slp_balance = slp_utils.get_claimed_slp(account_address)

    if slp_balance == 0:
        log("({}/{}) Skipping account {} ({}) because SLP balance is zero.".format(curr_index, num_accounts, scholar_name, format_ronin_address(account_address)))
        continue

    scholar_payout_percentage = float(scholar_info[4])
    if not (0 < scholar_payout_percentage <= 1):
        log(message="Scholar payout percentage not correctly entered for {}".format(scholar_name), error=True)
    assert(0 < scholar_payout_percentage <= 1)

    scholar_payout_amount = math.ceil(slp_balance * scholar_payout_percentage)
    academy_payout_amount = slp_balance - scholar_payout_amount

    assert (scholar_payout_amount >= 0)
    assert (academy_payout_amount >= 0)
    assert (slp_balance == scholar_payout_amount + academy_payout_amount)

    payouts.append(Payout(
        name=scholar_name,
        private_key=get_private_key(scholar_info[2]),
        slp_balance=slp_balance,
        nonce=nonces[account_address],
        scholar_transaction=Transaction(from_address=account_address, to_address=scholar_payout_address,
                                        amount=scholar_payout_amount),
        academy_transaction=Transaction(from_address=account_address, to_address=academy_payout_address,
                                        amount=academy_payout_amount)))

log()

if len(payouts) == 0:
    exit()

# Preview transactions.
num_payouts = len(payouts)
curr_payout = 0
for payout in payouts:
    curr_payout += 1
    log("({}/{}) Payout for {}".format(curr_payout, num_payouts, payout.name))
    log(f"├─ SLP balance: {payout.slp_balance} SLP")
    log(f"├─ Nonce: {payout.nonce}")
    log(
        f"├─ Scholar payout: send {payout.scholar_transaction.amount:5} SLP from {format_ronin_address(payout.scholar_transaction.from_address)} to {format_ronin_address(payout.scholar_transaction.to_address)}")
    log(
        f"├─ Academy payout: send {payout.academy_transaction.amount:5} SLP from {format_ronin_address(payout.academy_transaction.from_address)} to {format_ronin_address(payout.academy_transaction.to_address)}")
    log()

log("Would you like to execute transactions? [y]/N", end=" ")
if input() != "y":
    log("No transaction was executed. Program will now stop.")
    exit()

# Execute transactions.
log()
log("Executing transactions...")
for payout in payouts:
    log(f"Executing payout for '{payout.name}'")
    log(
        f"├─ Scholar payout: sending {payout.scholar_transaction.amount} SLP from {format_ronin_address(payout.scholar_transaction.from_address)} to {format_ronin_address(payout.scholar_transaction.to_address)}...",
        end="")
    log(f"├─ Send? [y]/N", end="")
    txn_hash = slp_utils.transfer_slp(payout.scholar_transaction, payout.private_key, payout.nonce)
    time.sleep(0.250)
    log("DONE")
    log(f"│  Hash: {txn_hash} - Explorer: https://explorer.roninchain.com/tx/{str(txn_hash)}")

    log(
        f"├─ Academy payout: sending {payout.academy_transaction.amount} SLP from {format_ronin_address(payout.academy_transaction.from_address)} to {format_ronin_address(payout.academy_transaction.to_address)}...",
        end="")
    log(f"├─ Send? [y]/N", end="")
    txn_hash = slp_utils.transfer_slp(payout.academy_transaction, payout.private_key, payout.nonce + 1)
    time.sleep(0.250)
    log("DONE")
    log(f"│  Hash: {txn_hash} - Explorer: https://explorer.roninchain.com/tx/{str(txn_hash)}")
    log()
