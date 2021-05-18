import re, time, binascii
from random_word import RandomWords
import Mnemonic_util as imMnemonic

while True:
    ranWords = RandomWords()    
    # ranWords.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minCorpusCount=1, maxCorpusCount=10, minDictionaryCount=1, maxDictionaryCount=10, minLength=3, maxLength=8, sortBy="alpha", sortOrder="asc", limit=12)
    # Lowercase List Strings    
    words = list(map(lambda x: x.lower(), ranWords.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minLength=3, maxLength=8, sortBy="alpha", sortOrder="asc", limit=12)))
    # Removing-special-characters-from-a-list-of-items
    amendWords = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in words]
    # Convert a list to string using list comprehension    
    seedPhraseValue = ' '.join([str(elem) for elem in amendWords])
    print(seedPhraseValue)
    biPrivateKey = imMnemonic.mnemonic_to_private_key(seedPhraseValue)    
    print("Your private key is: {}".format(str(binascii.hexlify(biPrivateKey), 'utf-8')))
    time.sleep(3)    

