import json, binascii, subprocess, asyncio
import pandas as pd
from web3 import Web3
from web3.auto import w3
from decouple import config

# Global variables
NETWORK_HOME = config('NETWORK_NAME')
ACCOUNT_FILE = config('KEY_FILE')
ACCOUNT_KEY = config('KEY')
P_KEY = config('PASS_KEY')
KEY_BASE = config('KEYSTORE_BASE')
KEY_HOME = config('KEYSTORE_HOME')
ALL_KEY = config('ALL_KEY_FILE')
PRIVATE_KEY = config('PRIVATE_KEY_FILE')
MNEMONIC_STRING = config('MNEMONIC')

# Connection Verification
web3 = Web3(Web3.HTTPProvider(NETWORK_HOME))

# Function to return balances of ethereum
def toEther(balance):    
    return web3.fromWei(balance, 'ether')


# Fucntion to calling account and printing all accounts' balances
def listAccounts():        
    for idx, account in enumerate(web3.eth.accounts):                        
        print(f'[{idx+1}] Balance of {account} : {toEther(web3.eth.getBalance(account))} ETH')


# Function to extract all accounts from Ganache-cli
async def extractAccounts():     
    subprocess.Popen(['ganache-cli', '-m', MNEMONIC_STRING, '--account_keys_path', ALL_KEY], text=True, stdout=subprocess.PIPE)
    await asyncio.sleep(5)
    # Create temporary type-in key_file    
    with open(P_KEY, 'w') as pfile:        
        pfile.write(ACCOUNT_KEY)
        pfile.close() 


# Function to attach accounts in ETHEREUM_HOME
def addAcounts():     
    with open(ALL_KEY, 'r+') as kf:
        info_json = json.load(kf)
        kf.close()

    # _address = info_json["addresses"]
    # print("Account_Address :", _address)
    _private_keys = info_json['private_keys']
    # print("Private_Keys :", _private_keys)
    with open(PRIVATE_KEY, 'w') as outfile:
        json.dump(_private_keys, outfile)

    # Attach accounts from json key file
    df = pd.read_json(PRIVATE_KEY, typ='private_keys')
    # print(df.to_string())    
    i = 0
    while i < len(df.index):
        with open(PRIVATE_KEY, 'w+') as pf:            
            print("Private_Key :", df.iloc[i])            
            pf.write(df.iloc[i])                               
            subprocess.Popen(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', P_KEY, PRIVATE_KEY], text=True, stdout=subprocess.PIPE)
            i += 1            


# Function to list accounts from Geth
def listGethAccounts():        
    subprocess.run(["geth", "account", "list", "--keystore", KEY_HOME])
    # Delete the key files    
    subprocess.Popen(['rm', '-rf', ALL_KEY], text=True, stdout=subprocess.PIPE)
    subprocess.Popen(['rm', '-rf', PRIVATE_KEY], text=True, stdout=subprocess.PIPE)
    subprocess.Popen(['rm', '-rf', P_KEY], text=True, stdout=subprocess.PIPE)
      

# Function to account creation with images
def accountCreation(account_num):
    web3.eth.defaultAccount = web3.eth.accounts[account_num]
    print("Default Account:", web3.eth.defaultAccount)

    # # Identicon Setup the padding(top, bottom, left, right) in pixels.
    # padding = (10, 10, 10, 10)
    # identicon_png = icon.generator.generate(web3.eth.defaultAccount, 20, 20, padding=padding, output_format="png")
    # # Identicon can be easily saved to a file.
    # f = open("static/images/%s.png" % (web3.eth.defaultAccount), "wb")
    # f.write(identicon_png)
    # f.close()
    # #Creating an instance of QRCode image
    # qr = qrcode.QRCode(version=1, box_size=5, border=5)
    # qr.add_data(web3.eth.defaultAccount)
    # qr.make(fit=True)
    # img = qr.make_image(fill='black', back_color='white')
    # img.save('static/images/%s_qrcode.png' % (web3.eth.defaultAccount))

    return web3.eth.defaultAccount


with open(ACCOUNT_FILE) as f:
    info_json = json.load(f)

_address = info_json["address"]
_address = web3.toChecksumAddress(_address)
_cipher = info_json["crypto"]["ciphertext"]

print("Account_Address :", _address)
print("Account_Cipher :", _cipher)

with open(ACCOUNT_FILE) as keyfile:
    _encrypted_key = keyfile.read()
    _decrypted_key = w3.eth.account.decrypt(_encrypted_key, ACCOUNT_KEY)

_private_key = binascii.b2a_hex(_decrypted_key)
balance = web3.eth.getBalance(_address)
print("Private_Key :", _private_key.decode('ascii'))
print("Connections :", web3.isConnected())
print("Current_Block # :", web3.eth.blockNumber)
print("Ether Balance :", toEther(balance),"ETH")


async def main():
    # List accounts
    # listAccounts()
    await extractAccounts()    
    addAcounts()
    listGethAccounts()

asyncio.run(main())


