import json, binascii, requests, glob
from web3 import Web3
from web3.auto import w3
from decouple import config

# Global variables
NETWORK_HOME = config('NETWORK_NAME_DEV')
KFILE_HOME = config('KEYFILE_HOME')
ACCOUNT_FILE = config('KEY_FILE')
ACCOUNT_KEY = config('KEY')
API_URL = config('ETHSCAN_URL')
_global_decrypted_key = ''
_global_wallet_addresses = ''
_global_principal_address = ''
_global_wallet_address_counts = 0


# Connection Verification
web3 = Web3(Web3.HTTPProvider(NETWORK_HOME))
# print("Established_Connections :", web3.isConnected())
# print("Current_Block # :", web3.eth.blockNumber, "\n")


# Get the current price of cryptocurrency conversion API URL
req = requests.get(API_URL)
# print(json.loads(req.content))
USD_CURRENCY=json.loads(req.content)["USD"]


# Function to return balances of ethereum
def toEther(balance):    
    return web3.fromWei(balance, 'ether')


# Function to return USD conversion values
def toUSD(balance):
    usd_sum = round(USD_CURRENCY * float(toEther(balance)), 2)    
    return usd_sum


# Function to return Trans USD conversion values
def toTransUSD(balance):
    usd_trans_sum = USD_CURRENCY * float(balance)          
    return str(usd_trans_sum)[:str(usd_trans_sum).index(".") + 3] 
    

# Function to extract all accounts from geth
def extractAccounts(): 
    # Change the glob if you want to only look through files with specific names
    files = glob.glob(f'{KFILE_HOME}/*', recursive=True)

    # Loop through multiple files    
    for idx, single_file in enumerate(files):
        with open(single_file, 'r') as sf:            
            json_file = json.load(sf)     
            global _global_wallet_addresses, _global_wallet_address_counts                   
            _global_wallet_addresses = web3.toChecksumAddress(json_file["address"])
            _cipher = json_file["crypto"]["ciphertext"]
            # print(single_file)                        
            print(f"[{idx+1}]Account_Address : {_global_wallet_addresses}")
            print("Account_Cipher :", _cipher)
            _global_wallet_address_counts += 1
            sf.close()
                        
        with open(single_file, 'r') as keyfile:        
            _encrypted_key = keyfile.read()            
            balance = web3.eth.getBalance(_global_wallet_addresses)
            print("Private_Key :", binascii.b2a_hex(w3.eth.account.decrypt(_encrypted_key, ACCOUNT_KEY)).decode('ascii'))    
            print("Ether Balance :", toEther(balance),"ETH =",toUSD(balance),"$USD\n")            
            keyfile.close()


# Function to select principle account
def selectPrincipalAccount(): 
    # Change the glob if you want to only look through files with specific names
    files = glob.glob(f'{KFILE_HOME}/*', recursive=True)
    # Define the principle address   
    global _global_principal_address, _global_decrypted_key
    _principal_Address = []    
    _principal_private_key = []
    sen_num = input("\nSelect your principle address[#]: ")            
    # Loop through multiple files        
    if((int(sen_num) > 0) and (int(sen_num) <= _global_wallet_address_counts)):                
        for idx, single_file in enumerate(files):
            with open(single_file, 'r') as sf:           
                json_file = json.load(sf)                     
                _principal_Address.insert(idx, web3.toChecksumAddress(json_file["address"]))                        
                sf.close()

                with open(single_file, 'r') as keyfile:        
                    _encrypted_key = keyfile.read()                    
                    _principal_private_key.insert(idx, w3.eth.account.decrypt(_encrypted_key, ACCOUNT_KEY))                                                             
                    keyfile.close()                            

        _global_principal_address = _principal_Address[int(sen_num)-1]
        print(f"Selected Principal Account Address : {_principal_Address[int(sen_num)-1]}\n")        
        _global_decrypted_key = _principal_private_key[int(sen_num)-1]
        # print(f"Selected Principal Private Binary Key : {_principal_private_key[int(sen_num)-1]}\n")        
    else:            
        print('Wrong Principle Account Selection.')  
        exit()    


# Fucntion to calling account and printing all accounts' balances
def listAccounts():        
    for idx, account in enumerate(web3.eth.accounts):                
        print(f'[{idx+1}] Balance of {account} : {toEther(web3.eth.getBalance(account))} ETH')            


# Function to transfer ethereum
def sendEther(rec_num, donor_addr):
    # Define the recipient address     
    recipient_Address = ''
    if(int(rec_num) > 0 and int(rec_num) <= len(web3.eth.accounts)):
        for idx in range(len(web3.eth.accounts)):
            if(idx == (int(rec_num)-1)): recipient_Address = web3.eth.accounts[idx]
        idx += 1 
    else:
        print('Wrong Recipient Account Selection.')            
        exit()

    # Input Recipient Amount
    amounts = input("Enter your amounts of ethererum(ETH): ")        
      
    # get the nounce
    nonce = web3.eth.getTransactionCount(donor_addr)

    # build a transaction
    tx = {
        'nonce': nonce,
        'to': recipient_Address,        
        'value': web3.toWei(amounts, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei')
    }

    # sign a transaction
    signed_tx = web3.eth.account.signTransaction(tx, _global_decrypted_key)

    # send a transaction
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # decodes the transaction data    
    print("\nTransaction Number:", web3.toHex(tx_hash))    
    print("From:", web3.eth.getTransactionReceipt(tx_hash)['from'], ", To:", web3.eth.getTransactionReceipt(tx_hash)['to'])               
    print("Transaction Amount:", web3.eth.getTransaction(tx_hash)['value'], "Wei (", toEther(web3.eth.getTransaction(tx_hash)['value']),"ETH =", toTransUSD(toEther(web3.eth.getTransaction(tx_hash)['value'])),"$USD) , GasPrice:", web3.eth.getTransaction(tx_hash)['gasPrice'])
    print("GasUsed:", web3.eth.getTransactionReceipt(tx_hash)['gasUsed'])
    print(web3.eth.getTransactionReceipt(tx_hash)['status']==1 and "The transaction was successful." or "The transaction was reverted by EVM.")


# List Accounts Info Display
extractAccounts()
selectPrincipalAccount()
listAccounts()
# Input Recipient Address
rec_num = input("\nSelect your recipient address[#]: ")
# Transfer Ether Function
sendEther(rec_num, _global_principal_address)
