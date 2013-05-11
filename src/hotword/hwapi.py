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

