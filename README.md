# SS-DAMG-Bot
- SS-DAMG Bot is a bot that performs various tasks to suppport the SS-DAMG discord community.

# TODO:
2. Payout script
4. Make a channel for dev projects
5. Fully clean out this codebase to be ss-damgs
6. Axie Market bot API
7. Make a projects list somewhere
8. Abstract out the original code so I can send messages to users/channels easier
9. A reward for reaching a team average of a certain level.
10. Mutation odds calculator

Unnecessary Ideas:
2. Make a scraper to check all the discord ids
3. remove names from secret scholar, get them from the discord channel
3. Could have bot read out when someone's rating goes up, reaches a threshold in SLP, etc.

Commands:
$qr
!rank
!rank top (only for founders)

## Encryption:
To add new scholars to the scholar store, you must:
1. Decrypt the CSV using the encryption key. I recommend making the output file somewhere that isn't inside the repository locally so you don't accidentally add it to the repo. The command I'll be using is below: 
```
python encryption.py -m decrypt -i ~/repos/ss-damg-bot/scholar_store_encrypted.csv -o ~/Desktop/scholar_store_decrypted_DO_NOT_ADD.csv -k <encryption_key>
```
2. Make your changes to the CSV
3. Encrypt the CSV back into the repo. The command I'll be using is here:
```
python encryption.py -m encrypt -i ~/Desktop/scholar_store_decrypted_DO_NOT_ADD.csv -o ~/repos/ss-damg-bot/scholar_store_encrypted.csv  -k <encryption_key>
```

The general commands are as follows:

Encrypt:
```
python encryption.py -m encrypt -i <path_to_decrypted_file> -o <path_where_encrypted_file_should_be_created> -k <encryption_key>
```
Decrypt:
```
python encryption.py -m decrypt -i <path_to_encrypted_file> -o <path_where_decrypted_file_should_be_created> -k <encryption_key>
```
Generate new key:
```
 python encryption.py -m genkey
```
Your key is everything inside the single quotes (not the b or the either of the 's)

## Payout:
The payout bot will claim SLP in the addresses within your encrypted scholar store, and then pay out the earnings to both
your address and your scholars addresses (using the scholar payout address database).

The command to run it is as follows: 
```
python ss-damg-payout.py scholar_store_encrypted.csv
```