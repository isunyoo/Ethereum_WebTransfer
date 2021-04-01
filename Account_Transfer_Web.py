import json, binascii, requests, glob
from web3 import Web3
from web3.auto import w3
from decouple import config
from flask import Flask, render_template, request, redirect, url_for

ganache_url = "HTTP://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

KFILE_HOME = config('KEYFILE_HOME')
ACCOUNT_FILE = config('KEY_FILE')
ACCOUNT_KEY = config('KEY')
API_URL = config('ETHSCAN_URL')

# Global variables
_global_decrypted_key = ''
_global_principal_address = ''
_global_recipient_address = ''
_global_wallet_address_counts = 0
_global_wallet_addresses = []
_global_wallet_balances = []
_global_wallet_balance_ether = []
_global_wallet_balance_usd = []
_global_addresses_cipher = []
_recipient_wallet_addresses = []
_recipient_wallet_balance_ether = []
_recipient_wallet_balance_usd = []


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


# Function to extract all accounts from geth
def extractAccounts():     
    # Change the glob if you want to only look through files with specific names
    files = glob.glob(f'{KFILE_HOME}/*', recursive=True)

    # clearing the lists
    _global_wallet_addresses.clear()            
    _global_addresses_cipher.clear()
    _global_wallet_balances.clear()            
    _global_wallet_balance_ether.clear()       
    _global_wallet_balance_usd.clear()          

    # Loop through multiple files    
    for idx, single_file in enumerate(files):
        with open(single_file, 'r') as sf:            
            json_file = json.load(sf)                 
            global _global_wallet_address_counts                   
            _global_wallet_addresses.insert(idx, web3.toChecksumAddress(json_file["address"]))            
            _global_addresses_cipher.insert(idx, json_file["crypto"]["ciphertext"])            
            # print("Account_Cipher :", _global_addresses_cipher[idx])
            _global_wallet_address_counts += 1
            sf.close()
                        
        with open(single_file, 'r') as keyfile: 
            _encrypted_key = keyfile.read()             
            _global_wallet_balances.insert(idx, web3.eth.getBalance(_global_wallet_addresses[idx]))
            _global_wallet_balance_ether.insert(idx, str(toEther(_global_wallet_balances[idx])))
            _global_wallet_balance_usd.insert(idx, toUSD(_global_wallet_balances[idx]))
            # print("Private_Key :", binascii.b2a_hex(w3.eth.account.decrypt(_encrypted_key, ACCOUNT_KEY)).decode('ascii'))                     
            # print("Ether Balance :", toEther(_global_wallet_balances[idx]),"ETH =",toUSD(_global_wallet_balances[idx]),"$USD\n")     
            keyfile.close()
    
    return _global_wallet_addresses, _global_addresses_cipher, _global_wallet_balance_ether, _global_wallet_balance_usd


# Function to extract principal account cipher
def extractPrincipalCipher(principalAddress):     
    # Local Lists variables
    _principal_addresses_cipher = ''
    _local_principal_addresses = []
    _local_principal_addresses_cipher = []    

    # Change the glob if you want to only look through files with specific names
    files = glob.glob(f'{KFILE_HOME}/*', recursive=True)
    
    # Loop through multiple files    
    for idx, single_file in enumerate(files):
        with open(single_file, 'r') as sf:            
            json_file = json.load(sf)                                             
            _local_principal_addresses.insert(idx, web3.toChecksumAddress(json_file["address"]))            
            _local_principal_addresses_cipher.insert(idx, json_file["crypto"]["ciphertext"])                        
            sf.close()
        if(str(principalAddress) == str(_local_principal_addresses[idx])): _principal_addresses_cipher = _local_principal_addresses_cipher[idx]            
        
    return _principal_addresses_cipher


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
    # clearing the lists
    _recipient_wallet_addresses.clear()            
    _recipient_wallet_balance_ether.clear()
    _recipient_wallet_balance_usd.clear()
    for idx, account in enumerate(web3.eth.accounts):
        _recipient_wallet_addresses.insert(idx, account)
        _recipient_wallet_balance_ether.insert(idx, str(toEther(web3.eth.getBalance(account))))
        _recipient_wallet_balance_usd.insert(idx, toUSD(web3.eth.getBalance(account)))
        print(f'[{idx+1}] Balance of {account} : {toEther(web3.eth.getBalance(account))} ETH')

    return _recipient_wallet_addresses, _recipient_wallet_balance_ether, _recipient_wallet_balance_usd


# Function to transfer console ethereum
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

    # Function to transfer web ethereum
def sendWebEther(reci_addr, donor_addr, amounts):
    # Define the recipient address     
    recipient_Address = str(reci_addr)
      
    # get the nounce
    nonce = web3.eth.getTransactionCount(str(donor_addr))

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


# Connection Verification
print("Established_Connections :", web3.isConnected())
print("Current_Block # :", web3.eth.blockNumber, "\n")
# # List Accounts Info Display
# extractAccounts()
# selectPrincipalAccount()
# listAccounts()
# # Input Recipient Address
# rec_num = input("\nSelect your recipient address[#]: ")
# # Transfer Ether Function
# sendEther(rec_num, _global_principal_address)


# Flask http web display
app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = '12345'

@app.route('/', methods=['GET', 'POST'])
def index():    
    account_name = extractAccounts()
    dataLen = len(account_name)
    print(account_name)    
    # print(account_name[1])       
    # initial_hello = getHelloFromBlockchain()    
    # initial_length = getLengthFromBlockchain()
    # initial_contents = getContentsFromBlockchain()
    # initial_sum = getSumFromBlockchain()    
    # return render_template('index.html', value0=default_account, value1=initial_hello, value2=initial_length, value3=initial_contents, value4=initial_sum)
    return render_template('index.html', value0=account_name, value1=dataLen)    
        
@app.route('/selectPrincipalData', methods=['POST'])
def selectPrincipalInput():
    global _global_principal_address
    principalAddress = request.form['principle']
    _global_principal_address = principalAddress    
    print(extractPrincipalCipher(principalAddress))    
    recipientLists = listAccounts()    
    dataLen = len(recipientLists[0])            
    # return redirect(url_for('index'))
    return render_template('recipient_display.html', value0=principalAddress, value1=recipientLists, value2=dataLen)

@app.route('/sendEther', methods=['POST'])
def selectRecipientInput():
    global _global_recipient_address
    principalAddress = _global_principal_address
    recipientAddress = request.form.getlist('recipient')  
    _global_recipient_address = recipientAddress
    # print("Selected Recipient Data :", recipientAddress)    
    return render_template('ether_display.html', value0=principalAddress, value1=recipientAddress)

@app.route('/transferEther', methods=['POST'])
def etherTransaction():    
    principalAddress = _global_principal_address
    recipientAddress = _global_recipient_address 
    etherAmount = request.form.getlist('inputEtherValue') 
    print(principalAddress, recipientAddress, etherAmount)
    sendWebEther(recipientAddress, principalAddress, etherAmount)
    # print("Selected Recipient Data :", recipientAddress)    
    # return render_template('ether_display.html', value0=principalAddress, value1=recipientAddress)
    return redirect(url_for('index'))
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)