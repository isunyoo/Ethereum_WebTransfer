import json, subprocess
import pandas as pd
from decouple import config

# Global variables
P_KEY = config('KEY')
KEY_BASE = config('KEYSTORE_BASE')
PRIVATE_KEY = config('PRIVATE_KEY_FILE')

# Function to attach account in ETHEREUM_HOME
def importPrivateKey(private_key):        
    with open(PRIVATE_KEY, 'w') as outfile:        
        outfile.write(json.dumps(private_key).replace('"', ''))    
        status = subprocess.Popen(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', P_KEY, PRIVATE_KEY], text=True, stdout=subprocess.PIPE)        
        status.communicate()
    return status.returncode

    # # Attach accounts from json key file
    # df = pd.read_json(PRIVATE_KEY, typ='private_keys')
    # # print(df.to_string())    
    # i = 0
    # while i < len(df.index):
    #     with open(PRIVATE_KEY, 'w+') as pf:            
    #         print("Private_Key :", df.iloc[i])            
    #         pf.write(df.iloc[i])                               
    #         # subprocess.Popen(['geth', 'account', 'import', '--datadir', KEY_BASE, PRIVATE_KEY], text=True, stdout=subprocess.PIPE)
    #         subprocess.Popen(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', P_KEY, PRIVATE_KEY], text=True, stdout=subprocess.PIPE)
    #         i += 1 

