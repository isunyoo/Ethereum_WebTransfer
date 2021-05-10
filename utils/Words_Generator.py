from random_word import RandomWords
r = RandomWords()
words = r.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minCorpusCount=1, maxCorpusCount=10, minDictionaryCount=1, maxDictionaryCount=10, minLength=4, maxLength=8, sortBy="alpha", sortOrder="asc", limit=12)
print(words)
