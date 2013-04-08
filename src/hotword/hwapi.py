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
            'link': {
                    'href': webapp2.uri_for('search', keyword=_getKeywords(word)),
                    'target': '_blank',
                    'title': word['page'],
                },
            })
    latestWords = []
    for word in data.get('latest', {}).get('words', []):
        title = _getKeywords(word)
        latestWords.append({
            'title': title,
            'url': webapp2.uri_for('search', keyword=title),
        })
    return json.dumps({
            'all': allWords,
            'latest': latestWords,
        })

