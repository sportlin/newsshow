from . import models

def getWords(wordsName):
    data = models.getWords(wordsName)
    allWords = []
    pages = []
    urls = set()
    for word in data.get('words', []):
        url = word['page'].get('url')
        if url in urls:
            continue
        urls.add(url)
        allWords.append({
            'keywords': word['readablekeywords'][:3],
            'weight': word['size'],
            })
        word['page']['keywords'] = word['readablekeywords']
        word['page']['weight'] = word['size']
        pages.append(word['page'])

    _WORDS_SIZE = 30
    allWords.sort(key=lambda word: len(word['keywords']), reverse=True)
    allWords.sort(key=lambda word: word['weight'], reverse=True)
    allWords = allWords[:_WORDS_SIZE]

    return allWords, pages

