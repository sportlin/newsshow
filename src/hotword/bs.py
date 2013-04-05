import datetime

from commonutil import dateutil

from sourcenow import snapi
from . import models

def calculateTopWords():
    import jieba # May fail to load jieba
    pages = snapi.getSitePages()
    words = []
    titles = []
    for page in pages:
        title = page.get('title')
        if not title:
            continue
        titles.append(title)
    pwords = jieba.cut('\n'.join(titles), cut_all=False)

    for word in pwords:
        if len(word) > 1:
            words.append(word)
    words.sort()

    lastWord = None
    lastCount = 0
    result = []
    _MIN_WORD_COUNT = 4
    for word in words:
        if lastWord != word:
            if lastCount >= _MIN_WORD_COUNT:
                result.append({'w': lastWord, 'c': lastCount})
            lastWord = word
            lastCount = 0
        lastCount += 1
    if lastCount >= _MIN_WORD_COUNT:
        result.append({'w': lastWord, 'c': lastCount})

    result.sort(key=lambda item: item.get('c'), reverse=True)
    return result

def saveWords(items):
    nnow = datetime.datetime.utcnow()
    data = {
            'updated': dateutil.getDateAs14(nnow),
            'words': items,
        }
    models.saveWords(data)

def getWords():
    value = models.getWords()
    return value.get('words', [])

