import json

import webapp2

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

def getJsonWords():
    data = bs.getWords('sources')
    allWords = []
    for word in data.get('all', {}).get('words', []):
        allWords.append({
            'text': _getTitle(word),
            'weight': word['page'],
            'keyword': _getKeywords(word),
            })
    latestWords = []
    for word in data.get('latest', {}).get('words', []):
        title = _getKeywords(word)
        latestWords.append({
            'title': title,
        })
    return json.dumps({
            'all': allWords,
            'latest': latestWords,
        })

