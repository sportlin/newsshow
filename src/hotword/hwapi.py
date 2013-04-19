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
        word['page']['weight'] = word['pages']
        pages.append(word['page'])

    _WORDS_SIZE = 30
    allWords.sort(key=lambda word: len(word['keywords']), reverse=True)
    allWords.sort(key=lambda word: word['pages'], reverse=True)
    allWords = allWords[:_WORDS_SIZE]

    return allWords, pages

