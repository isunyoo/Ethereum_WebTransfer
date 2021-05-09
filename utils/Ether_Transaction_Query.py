#!/usr/bin/python
import web3, json, os, glob, yaml
from web3 import Web3
from decouple import config
from hexbytes import HexBytes

# Global variables
NETWORK_HOME = config('NETWORK_NAME_DEV')

# Connection Verification
web3 = Web3(Web3.HTTPProvider(NETWORK_HOME))

# Exports transactions to a JSON file where each line contains the data returned from the JSONRPC interface
def tx_to_json(tx):
    result = {}
    for key, val in tx.items():
        if isinstance(val, HexBytes):
            result[key] = val.hex()
        else:
            result[key] = val    
    return json.dumps(result)

# Function to Retrieve Tx results historical data as json file
def queryEther(query_file, start_block, end_block, account_address):      

    # Delete all history transaction files
    files = glob.glob('static/query/*.json')
    for f in files:
        os.remove(f)

    address_lowercase = account_address.lower()
    ofile = open('static/query/'+query_file+'.json', 'w')    
    ofile.write('[')

    for idx in range(start_block, end_block):
        # print('Fetching block %d, remaining: %d, progress: %d%%'%(idx, (end_block-idx), 100*(idx-start_block)/(end_block-start_block)))
        
        block = web3.eth.getBlock(idx, full_transactions=True)

        for tx in block.transactions:
            
            if tx['to']:
                to_matches = tx['to'].lower() == address_lowercase
            else:
                to_matches = False

            if tx['from']:
                from_matches = tx['from'].lower() == address_lowercase
            else:
                from_matches = False

            if to_matches or from_matches:
                # print('Found transaction with hash %s'%tx['hash'].hex())                                
                ofile.write(tx_to_json(tx)+',')                            
                ofile.flush()

    ofile.write(']')    
    ofile.close()

    # Re-align JsonFile Format
    data = yaml.safe_load(open(ofile.name))    
    with open('static/query/'+query_file+'.json', 'w') as json_file:        
        json.dump(data, json_file, indent = 14, sort_keys=True)
    json_file.close()    

    return ofile.name
