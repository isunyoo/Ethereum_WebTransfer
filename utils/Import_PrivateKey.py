import pandas as pd
import json, subprocess, os, glob
from decouple import config
from sys import stderr, stdout
from werkzeug.utils import secure_filename

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
        # Run External Shell Programs for geth command    
        status = subprocess.run(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', pfile.name, outfile.name], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

    # Delete all Key files        
    files = glob.glob(KEY_BASE+'/temp/*')
    for f in files:
        os.remove(f)

    return status.returncode, status.stdout


# Function that check if an extension is valid and that uploads the file 
def allowed_file(filename):
    # Set of allowed file extensions
    ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Function to upload privateKey file in ETHEREUM_HOME
def uploadPrivateKey(privatekey_file): 
    UPLOAD_FOLDER = config('UPLOAD_FOLDER')
    
    # Uploaded PrivateKey file
    filename = secure_filename(privatekey_file.filename)
    if filename != '':
        UPLOAD_EXTENSIONS = {'.txt', '.doc', '.docx', ''}        
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in UPLOAD_EXTENSIONS:
            return 1, "Upload file must be word(txt, doc) format."
        UPLOAD_FOLDER = config('UPLOAD_FOLDER')        
        privatekey_file.save(os.path.join(UPLOAD_FOLDER, filename))

        # Keyphrase file creation
        pfile = open(UPLOAD_FOLDER+'passwdkey', 'w')
        pfile.write(P_KEY)
        pfile.close()
    
        # Read PrivateKey file
        ufile = open(UPLOAD_FOLDER+filename, 'r')    
        ufile.close()                              
        # Run External Shell Programs for geth command
        status = subprocess.run(['geth', 'account', 'import', '--datadir', KEY_BASE, '--password', pfile.name, ufile.name], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

        # Delete all Key files        
        files = glob.glob(UPLOAD_FOLDER+'*')
        for f in files:
            os.remove(f)

        return status.returncode, status.stdout

# https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask/page/3
