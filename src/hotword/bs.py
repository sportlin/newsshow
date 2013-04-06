# coding=utf-8

import datetime
import logging

from commonutil import dateutil

from sourcenow import snapi
from . import models

def _getTopWords(content):
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

def _getWordPages(pages, words):
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

def _mergeWord(wordTitles, parentWord, childWord):
    parentTitles = wordTitles[parentWord['name']]
    childTitles = wordTitles[childWord['name']]
    d = childTitles.difference(parentTitles)
    similar = len(d) * 1.0 / len(childTitles) < 0.6
    if similar:
        parentTitles.update(childTitles)
        parentWord['page'] = len(parentTitles)
        del wordTitles[childWord['name']]
    return similar

def _mergeWords(wordPages, words):
    index = 0
    size = len(words)
    while index < size:
        word = words[index]
        index2 = index + 1
        children = []
        while index2 < size:
            word2 = words[index2]
            if _mergeWord(wordPages, word, word2):
                children.append(word2)
                del words[index2]
                size -= 1
            else:
                index2 += 1
        if children:
            word['children'] = children
        index += 1

def calculateTopWords():
    pages = snapi.getSitePages()
    titles = []
    for page in pages:
        title = page.get('title')
        if not title:
            continue
        titles.append(title)
    words = _getTopWords('\n'.join(titles))
    wordPages = _getWordPages(pages, words)
    _mergeWords(wordPages, words)
    return words

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

