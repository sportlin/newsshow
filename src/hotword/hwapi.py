import json

from . import bs

def getJsonWords():
    words = bs.getWords()
    cloudWords = []
    for word in words:
        cloudWords.append({
            'text': word['w'],
            'weight': word['c'],
            'link': {
                    'href': '/search/' + word['w'],
                    'target': '_blank',
                    'title': word['c'],
                },
            })
    return json.dumps(cloudWords)

