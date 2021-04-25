import pandas as pd
from decouple import config
import json, subprocess, os, glob

# Global variables
P_KEY = config('KEY')
KEY_BASE = config('KEYSTORE_BASE')
PRIVATE_KEY = config('PRIVATE_KEY_FILE')

# Function to attach account in ETHEREUM_HOME
def importPrivateKey(private_key): 
    # Keyphrase file
    pfile = open(KEY_BASE+'/temp/passwdkey', 'w')
    pfile.write(P_KEY)
    pfile.close()    

    # PrivateKey file
    with open(PRIVATE_KEY, 'w') as outfile:        
        outfile.write(json.dumps(private_key).replace('"', ''))    
        status = subprocess.Popen(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', pfile.name, PRIVATE_KEY], text=True, stdout=subprocess.PIPE)        
        status.communicate()

    # Delete all Key files        
    files = glob.glob(KEY_BASE+'/temp/*')
    for f in files:
        os.remove(f)

    return status.returncode
