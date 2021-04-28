import pandas as pd
import json, subprocess, os, glob
from decouple import config
from sys import stderr, stdout
from werkzeug.utils import secure_filename
from flask import abort

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
        outfile.close()                                 
        status = subprocess.run(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', pfile.name, outfile.name], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

    # Delete all Key files        
    files = glob.glob(KEY_BASE+'/temp/*')
    for f in files:
        os.remove(f)

    return status.returncode, status.stdout


# Function to upload privateKey file in ETHEREUM_HOME
def uploadPrivateKey(privatekey_file): 
    # Keyphrase file
    KEY_BASE = config('KEYSTORE_BASE')
    pfile = open(KEY_BASE+'/temp/passwdkey', 'w')
    pfile.write(P_KEY)
    pfile.close()    

    # Uploaded PrivateKey file
    filename = secure_filename(privatekey_file.filename)
    if filename != '':
        # file_ext = os.path.splitext(filename)[1]
        # if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        #     abort(400)
        KEY_BASE = config('KEYSTORE_BASE')
        privatekey_file.save(os.path.join(KEY_BASE+'/temp/', filename))
    
        # Read PrivateKey file
        ufile = open(KEY_BASE+'/temp/'+filename, 'r')    
        ufile.close()                                
        status = subprocess.run(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', pfile.name, ufile.name], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

        # Delete all Key files        
        files = glob.glob(KEY_BASE+'/temp/*')
        for f in files:
            os.remove(f)

        return status.returncode, status.stdout