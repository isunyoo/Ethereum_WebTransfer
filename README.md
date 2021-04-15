# Ethereum_WebTransfer

from web3 import Web3\
ganache_url = "http://127.0.0.1:8545" \
web3 = Web3(Web3.HTTPProvider(ganache_url))

web3.eth.getBlock(web3.eth.blockNumber)\
web3.eth.getTransactionCount('account_address')

web3.eth.getTransaction(txhash)\
web3.eth.getTransaction(0xd03702cdf7cef045a2d9df443df81cd192a43006b2b06077d226b0f8ecc4e2b6)\
web3.eth.getTransactionReceipt(0xd03702cdf7cef045a2d9df443df81cd192a43006b2b06077d226b0f8ecc4e2b6)
