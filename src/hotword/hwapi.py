import json

import webapp2

from commonutil import stringutil

from . import bs

def _getTitle(word):
    words = [word['name']]
    if word.get('children'):
        words.append(word['children'][0]['name'])
    return ' '.join(words)

def _getKeywords(word):
    keywords = [word['name']]
    for item in word.get('children', []):
        keywords.append(item['name'])
    return ' '.join(keywords)

def getJsonWords(sentenceSeparators):
    data = bs.getWords('sources')
    allWords = []
    for word in data.get('all', {}).get('words', []):
        allWords.append({
            'text': _getTitle(word),
            'weight': word['pages'],
            'keyword': _getKeywords(word),
            })
    latestWords = []
    for word in data.get('latest', {}).get('words', []):
        if word['page'].get('content'):
            word['page']['content'] = stringutil.getFirstSentence(
                               sentenceSeparators, word['page']['content'])
        title = _getKeywords(word)
        word['page']['keyword'] = title
        latestWords.append(word['page'])
    return {
            'all': allWords,
            'latest': latestWords,
        }

