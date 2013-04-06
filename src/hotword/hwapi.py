import json

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
    words = bs.getWords()
    cloudWords = []
    for word in words:
        cloudWords.append({
            'text': _getTitle(word),
            'weight': word['page'],
            'link': {
                    'href': '/search/' + _getKeywords(word),
                    'target': '_blank',
                    'title': word['page'],
                },
            })
    return json.dumps(cloudWords)

