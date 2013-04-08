# coding=utf-8
import copy
import datetime
import logging


from commonutil import dateutil

from . import models

def getTopWords(pages):
    titles = []
    for page in pages:
        title = page.get('title')
        if not title:
            continue
        titles.append(title)
    content = '\n'.join(titles)

    import jieba # May fail to load jieba
    jieba.initialize(usingSmall=False)
    pwords = jieba.cut(content, cut_all=False)
    words = []
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
                result.append({'name': lastWord, 'count': lastCount})
            lastWord = word
            lastCount = 0
        lastCount += 1
    if lastCount >= _MIN_WORD_COUNT:
        result.append({'name': lastWord, 'count': lastCount})

    result.sort(key=lambda item: item.get('count'), reverse=True)
    return result

def _getWordTitles(pages, words):
    result = {}
    for word in words:
        wordTitles = set()
        for page in pages:
            title = page.get('title')
            if not title:
                continue
            if word['name'] in title:
                wordTitles.add(title)
        word['page'] = len(wordTitles)
        result[word['name']] = wordTitles
    return result

def _getSimilarValue(parentTitles, childTitles):
    i = childTitles.intersection(parentTitles)
    similar = len(i) * 1.0 / len(childTitles)
    return similar

def mergeWords(similarRate, pages, words):
    wordTitles = _getWordTitles(pages, words)
    index = 0
    size = len(words)
    while index < size:
        word = words[index]
        index2 = index + 1
        children = []
        parentTitles = wordTitles[word['name']]
        while index2 < size:
            word2 = words[index2]
            childTitles = wordTitles[word2['name']]
            similarValue = _getSimilarValue(parentTitles, childTitles)
            if similarValue >= similarRate:
                parentTitles.update(childTitles)
                word['page'] = len(parentTitles)
                del wordTitles[word2['name']]
                children.append(word2)
                del words[index2]
                size -= 1
                # the previous may be mergable after parent titles grow.
                index2 = index + 1
            else:
                index2 += 1
        if children:
            children.sort(key=lambda item: item['page'], reverse=True)
            word['children'] = children
        index += 1

def saveWords(similarRate, keyname, allHours, allWords, latestHours, latestWords):
    nnow = datetime.datetime.utcnow()
    data = {
            'similar': similarRate,
            'updated': dateutil.getDateAs14(nnow),
            'all': {
                'hours': allHours,
                'words': allWords,
            },
            'latest': {
                'hours': latestHours,
                'words': latestWords,
            },
        }
    models.saveWords(keyname, data)

def getWords(keyname):
    return models.getWords(keyname)

