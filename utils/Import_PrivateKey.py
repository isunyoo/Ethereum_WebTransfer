import json, subprocess, os, glob
import pandas as pd
from decouple import config

# Global variables
P_KEY = config('KEY')
KEY_BASE = config('KEYSTORE_BASE')
PRIVATE_KEY = config('PRIVATE_KEY_FILE')

# Function to attach account in ETHEREUM_HOME
def importPrivateKey(private_key): 
    pfile = open(KEY_BASE+'/temp/passwdkey', 'w')
    pfile.write(P_KEY)
    pfile.close()

    # save_path = '/home'
    # file_name = "test.txt"
    # completeName = os.path.join(save_path, file_name)
    # print(completeName)

    with open(PRIVATE_KEY, 'w') as outfile:        
        outfile.write(json.dumps(private_key).replace('"', ''))    
        status = subprocess.Popen(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', pfile, PRIVATE_KEY], text=True, stdout=subprocess.PIPE)        
        status.communicate()

        # Delete all PrivateKey files        
        # files = glob.glob(KEY_BASE+'/temp/*')
        # for f in files:
        #     os.remove(f)

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

