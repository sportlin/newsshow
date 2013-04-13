from . import bs

def calculateTopWords(wordsConfig, scope, pages):
    return bs.calculateWords(wordsConfig, scope, pages)

def getJsonWords(wordsName):
    data = bs.getWords(wordsName)
    allWords = []
    for word in data.get('words', []):
        allWords.append({
            'keywords': word['keywords'],
            'pages': word['pages'],
            })
    return allWords

