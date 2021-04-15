from web3 import Web3
from web3.auto import w3
from decouple import config
import Pydenticon_Generator as icon
import Ether_Transaction_Query as etherQuery
import json, binascii, requests, glob, qrcode, time
from flask import Flask, render_template, request, redirect, url_for, flash, Markup, Response, jsonify

ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

KFILE_HOME = config('KEYFILE_HOME')
ACCOUNT_FILE = config('KEY_FILE')
ACCOUNT_KEY = config('KEY')
API_URL = config('ETHSCAN_URL')

# Global variables
_global_principal_address = ''
_global_recipient_address = ''
_global_wallet_address_counts = 0
_global_wallet_addresses = []
_global_wallet_balances = []
_global_wallet_balance_ether = []
_global_wallet_balance_usd = []
_recipient_wallet_addresses = []
_recipient_wallet_balance_ether = []
_recipient_wallet_balance_usd = []


# Get the current price of cryptocurrency conversion API URL
req = requests.get(API_URL)
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


# Function to generate account images
def accountImageCreation(account_address):    
    # Identicon Setup the padding(top, bottom, left, right) in pixels.
    padding = (10, 10, 10, 10)
    identicon_png = icon.generator.generate(account_address, 20, 20, padding=padding, output_format="png")
    # Identicon can be easily saved to a file.
    f = open("static/images/%s.png" % (account_address), "wb")
    f.write(identicon_png)
    f.close()
    #Creating an instance of QRCode image
    qr = qrcode.QRCode(version=1, box_size=5, border=5)
    qr.add_data(account_address)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('static/images/%s_qrcode.png' % (account_address))  


# Function to extract all accounts from geth
def extractAccounts():     
    # Change the glob if you want to only look through files with specific names
    files = glob.glob(f'{KFILE_HOME}/*', recursive=True)

    # clearing the lists
    _global_wallet_addresses.clear()            
    _global_wallet_balances.clear()            
    _global_wallet_balance_ether.clear()       
    _global_wallet_balance_usd.clear()          

    # Loop through multiple files    
    for idx, single_file in enumerate(files):
        with open(single_file, 'r') as sf:            
            json_file = json.load(sf)                 
            global _global_wallet_address_counts                   
            _global_wallet_addresses.insert(idx, web3.toChecksumAddress(json_file["address"]))                        
            _global_wallet_address_counts += 1
            sf.close()                        
        with open(single_file, 'r') as keyfile: 
            _encrypted_key = keyfile.read()             
            _global_wallet_balances.insert(idx, web3.eth.getBalance(_global_wallet_addresses[idx]))
            _global_wallet_balance_ether.insert(idx, str(toEther(_global_wallet_balances[idx])))
            _global_wallet_balance_usd.insert(idx, toUSD(_global_wallet_balances[idx]))                      
            keyfile.close()
    
    return _global_wallet_addresses, _global_wallet_balance_ether, _global_wallet_balance_usd


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
            sf.close()
        with open(single_file, 'r') as keyfile: 
            _encrypted_key = keyfile.read()                         
            _local_principal_addresses_cipher.insert(idx, binascii.b2a_hex(w3.eth.account.decrypt(_encrypted_key, ACCOUNT_KEY)).decode('ascii')) 
            keyfile.close()
        if(str(principalAddress) == str(_local_principal_addresses[idx])): _principal_addresses_cipher = _local_principal_addresses_cipher[idx]            
        
    return _principal_addresses_cipher


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
        # print(f'[{idx+1}] Balance of {account} : {toEther(web3.eth.getBalance(account))} ETH')

    return _recipient_wallet_addresses, _recipient_wallet_balance_ether, _recipient_wallet_balance_usd


# Function to transfer web ethereum
def sendWebEther(reci_addr, donor_addr, amounts):    
          
    # get the nounce
    nonce = web3.eth.getTransactionCount(donor_addr)

    # build a transaction
    tx = {
        'nonce': nonce,
        'to': reci_addr,        
        'value': web3.toWei(amounts, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei')
    }
    
    # sign a transaction    
    signed_tx = web3.eth.account.signTransaction(tx, extractPrincipalCipher(donor_addr))    

    # send a transaction
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # decodes the transaction data 
    Tx_Status = web3.eth.getTransactionReceipt(tx_hash)['status']
    Tx_Num = web3.toHex(tx_hash)
    Frome = web3.eth.getTransactionReceipt(tx_hash)['from']
    To = web3.eth.getTransactionReceipt(tx_hash)['to']
    Wei_Amount = web3.eth.getTransaction(tx_hash)['value']
    Eth_Amount = toEther(web3.eth.getTransaction(tx_hash)['value'])
    Usd_Amount = toTransUSD(toEther(web3.eth.getTransaction(tx_hash)['value']))
    Gas_Fees_Wei = web3.eth.getTransaction(tx_hash)['gasPrice']
    Gas_Fees_Eth = '{:.8f}'.format(toEther(web3.eth.getTransaction(tx_hash)['gasPrice']))    
    Gas_Used = web3.eth.getTransactionReceipt(tx_hash)['gasUsed']    

    return Tx_Status, Tx_Num, Frome, To, Wei_Amount, Eth_Amount, Usd_Amount, Gas_Fees_Wei, Gas_Fees_Eth, Gas_Used


# Function of Tx results data 
def txResultData(tx_result):
    if(tx_result[0] == 1):              
        message = Markup(f'The transaction was successful for receipts.<br>Transaction Number: {tx_result[1]}<br>From: {tx_result[2]}<br>To: {tx_result[3]}<br>Transaction Amount: {tx_result[4]} Wei = {tx_result[5]} ETH = {tx_result[6]} $USD<br>GasPrice: {tx_result[7]} Wei = {tx_result[8]} ETH<br>GasUsed: {tx_result[9]}') 
        flash(message, 'results') 
    else:
        message = "The transaction was failed and reverted by EVM."
        flash(message, 'results') 


# Connection Verification
# print("Established_Connections :", web3.isConnected())
# print("Current_Block # :", web3.eth.blockNumber, "\n")

# Flask http web display
app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = '12345'

@app.route('/', methods=['GET', 'POST'])
def index():    
    account_name = extractAccounts()
    dataLen = len(account_name[0])    
    current_block = web3.eth.blockNumber
    # print(account_name)        
    return render_template('index.html', value0=account_name, value1=dataLen, value2=current_block)    
        
@app.route('/selectPrincipalData', methods=['POST'])
def selectPrincipalInput():
    global _global_principal_address    
    _global_principal_address = request.form['principle']
    # print(extractPrincipalCipher(principalAddress))    
    accountImageCreation(_global_principal_address)
    recipientLists = listAccounts()    
    dataLen = len(recipientLists[0])                    
    return render_template('recipient_display.html', value0=_global_principal_address, value1=recipientLists, value2=dataLen)

@app.route('/queryPrincipalData', methods=['POST'])
def queryPrincipalInput():
    global _global_principal_address    
    _global_principal_address = request.form['principle']    
    accountImageCreation(_global_principal_address)    
    start_block = int(request.form['fromBlk'])
    end_block = int(request.form['toBlk'])        
    # with open(etherQuery.queryEther(_global_principal_address, start_block, end_block, _global_principal_address), 'r') as dataContent:        
    #         json_file = json.load(dataContent)                                             
    #         print(json_file["hash"])
    #         dataContent.close()
    data = open(etherQuery.queryEther(_global_principal_address, start_block, end_block, _global_principal_address),'r')
    jsonFile = data.read()    
    print(jsonFile[0]['hash'])
    # queryOutput = json2html.convert(json = json.loads(jsonFile))
    # return render_template('query_display.html', value0=_global_principal_address, value1=start_block, value2=end_block, value3=queryOutput)
    return render_template('query_display.html', value0=_global_principal_address, value1=start_block, value2=end_block)
    
@app.route('/sendEther', methods=['POST'])
def selectRecipientInput():
    global _global_principal_address, _global_recipient_address    
    _global_recipient_address = request.form['recipient']    
    # print("Selected Recipient Data :", recipientAddress)       
    accountImageCreation(_global_recipient_address)        
    return render_template('ether_display.html', value0=_global_principal_address, value1=_global_recipient_address)

@app.route('/transferEther', methods=['POST'])        
def etherTransaction():        
    global _global_principal_address, _global_recipient_address        
    etherAmount = request.form['inputEtherValue']
    txResultData(sendWebEther(_global_recipient_address, _global_principal_address, etherAmount))           
    return redirect(url_for('index'))

@app.route('/convertUSD', methods=['GET'])
def convertUSD():                    
    convertedValue = request.args.get('inputEtherValue') 
    try:             
        if "".__eq__(convertedValue):
            return jsonify({'result': 0})    
        else:
            return jsonify({'result': toTransUSD(convertedValue)})      
    except ValueError:
        return jsonify({'result': 0})    

@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x < 100:            
            x = x + 10
            time.sleep(1.2)
            yield "data:" + str(x) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')    
    

# Development Debug Environment
if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)


# Production Environment
# if __name__ == "__main__":
#     from waitress import serve
#     serve(app, host="0.0.0.0", port=5000)