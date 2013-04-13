from . import bs

def calculateTopWords(wordsConfig, scope, pages):
    return bs.calculateWords(wordsConfig, scope, pages)

def getWords(wordsName):
    data = bs.getWords(wordsName)
    allWords = []
    pages = []
    for word in data.get('words', []):
        allWords.append({
            'keywords': word['keywords'],
            'pages': word['pages'],
            })
        word['page']['keywords'] = word['keywords']
        pages.append(word['page'])
    return allWords, pages

