#!/usr/bin/python
import web3, json, os, glob
from web3 import Web3
from hexbytes import HexBytes

ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Exports transactions to a JSON file where each line
# contains the data returned from the JSONRPC interface
def tx_to_json(tx):
    result = {}
    for key, val in tx.items():
        if isinstance(val, HexBytes):
            result[key] = val.hex()
        else:
            result[key] = val

    return json.dumps(result, indent = 14)


def queryEther(query_file, start_block, end_block, account_address):      

    # Delete all history transaction files
    files = glob.glob('static/query/*.json')
    for f in files:
        os.remove(f)

    address_lowercase = account_address.lower()
    ofile = open('static/query/'+query_file+'.json', 'w')    
    ofile.write('[')

    for idx in range(start_block, end_block):
        # print('Fetching block %d, remaining: %d, progress: %d%%'%(
        #     idx, (end_block-idx), 100*(idx-start_block)/(end_block-start_block)))

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
                # ofile.write(tx_to_json(tx)+'\n')                
                ofile.flush()

    ofile.write(']')    
    
    return ofile.name

    # https://stackoverflow.com/questions/50119663/add-character-and-remove-the-last-comma-in-a-json-file