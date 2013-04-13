# coding=utf-8
import copy
import datetime
import logging
import re

from commonutil import dateutil
import globalutil
from . import models


def _isStopWord(stopWordPatterns, word):
    stopped = False
    for pattern in stopWordPatterns:
        if re.match(pattern, word, re.IGNORECASE|re.DOTALL):
            stopped = True
            break
    return stopped

def getTopWords(pages, stopWordPatterns):
    titles = []
    for page in pages:
        keyword = page.get('keyword')
        if keyword:
            titles.append(keyword)
        title = page.get('title')
        if title:
            titles.append(title)
    content = '\n'.join(titles)

    import jieba # May fail to load jieba
    jieba.initialize(usingSmall=False)
    pwords = jieba.cut(content, cut_all=False)
    words = []
    for word in pwords:
        # sometime "\r\n\n" encountered
        word = word.strip()
        if not word:
            continue
        if not _isStopWord(stopWordPatterns, word):
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

    result.sort(key=lambda item: len(item['name']), reverse=True)
    result.sort(key=lambda item: item['count'], reverse=True)
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
        word['pages'] = len(wordTitles)
        result[word['name']] = wordTitles
    return result

def _isSimilarWords(similarCriterion, parentTitles, childTitles):
    total = len(childTitles)
    common = len(childTitles.intersection(parentTitles))
    if common == total:
        return True
    if not similarCriterion:
        return False
    threshhold = similarCriterion.get('0')
    if common >= threshhold:
        return True
    threshhold = similarCriterion.get(str(total))
    if not threshhold:
        return False
    return common >= threshhold

def _mergeWords(similarCriterion, pages, words):
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
            if len(childTitles) == 0:
                logging.warn('Empty child: %s' % (word2))
                index2 += 1
                continue
            if _isSimilarWords(similarCriterion, parentTitles, childTitles):
                parentTitles.update(childTitles)
                word['pages'] = len(parentTitles)
                del wordTitles[word2['name']]
                children.append(word2)
                del words[index2]
                size -= 1
                # the previous may be mergable after parent titles grow.
                index2 = index + 1
            else:
                index2 += 1
        if children:
            children.sort(key=lambda item: item['pages'], reverse=True)
            word['children'] = children
        index += 1

def _saveWords(keyname, allHours, allWords):
    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())
    data = {
            'updated': nnow,
            'hours': allHours,
            'words': allWords,
        }
    models.saveWords(keyname, data)

def getWords(keyname):
    return models.getWords(keyname)

def _populateWords(stopWords, similarCriterion, hours, pages):
    start = dateutil.getHoursAs14(hours)
    pages = [ page for page in pages if page['added'] >= start ]
    words = getTopWords(pages, stopWords)
    _mergeWords(similarCriterion, pages, words)
    for word in words:
        keywords = []
        keywords.append(word['name'])
        if word.get('children', []):
            keywords.append(word['children'][0]['name'])
        word['keywords'] = keywords

        matched = globalutil.search(pages, keywords)
        wordPage = max(matched, key=lambda page: page['grade'])
        word['page'] = wordPage
    return words

def calculateWords(wordsConfig, scope, pages):
    stopWords = wordsConfig['stop']
    similarCriterion = wordsConfig['similar']
    allHours = wordsConfig['hours.all']
    latestHours = wordsConfig['hours.latest']

    allWords = _populateWords(stopWords, similarCriterion, allHours, pages)
    latestWords = _populateWords(stopWords, similarCriterion, latestHours, pages)
    _saveWords(scope, allHours, allWords,)

    return allWords, latestWords

