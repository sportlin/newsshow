import datetime

from commonutil import dateutil
from . import models

def _summarizeEvent(scope, events, word, nnow):
    keywords = set(word['keywords'])
    matchedEvent = None
    for event in events['items']:
        if keywords.intersection(event['keywords']):
            matchedEvent = event
            break

    if not matchedEvent:
        matchedEvent = {}
        matchedEvent['id'] = events['counter']
        matchedEvent['added'] = nnow
        matchedEvent['keywords'] = set()

        events['items'].append(matchedEvent)
        events['counter'] += 1

    matchedEvent['updated'] = nnow
    matchedEvent['keywords'].update(word['keywords'])
    matchedEvent['word'] = word

def summarizeEvents(scope, words):
    events = models.getEvents(scope)
    if not events:
        events = {
            'counter': 0,
            'items': [],
        }

    for event in events['items']:
        event['keywords'] = set(event['keywords'])

    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())
    for word in words:
        _summarizeEvent(scope, events, word, nnow)

    for event in events['items']:
        event['keywords'] = list(event['keywords'])
    events['items'].sort(key=lambda item: item['word']['pages'], reverse=True)
    events['items'].sort(key=lambda item: item['updated'], reverse=True)
    models.saveEvents(scope, events)

def getEventPages(scope, size):
    events = models.getEvents(scope).get('items', [])
    events = events[:size]
    return [ event['word']['page'] for event in events ]

