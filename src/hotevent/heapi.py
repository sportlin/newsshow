import datetime

from commonutil import dateutil
from . import models

def _summarizeEvent(scope, events, word, nnow):
    createMinSize = 2
    keywords = set(word['keywords'])
    matchedEvent = None
    for event in events['items']:
        if keywords.intersection(event['keywords']):
            matchedEvent = event
            break

    if not matchedEvent and len(keywords) >= createMinSize:
        matchedEvent = {}
        matchedEvent['id'] = events['counter']
        matchedEvent['added'] = nnow
        matchedEvent['keywords'] = set()

        events['items'].append(matchedEvent)
        events['counter'] += 1

    if matchedEvent:
        matchedEvent['updated'] = nnow
        matchedEvent['keywords'].update(word['keywords'])
        matchedEvent['word'] = word

    return matchedEvent

def _saveEventItem(scope, eventId, word, nnow):
    eventItem = models.getEvent(scope, eventId)
    if not eventItem:
        eventItem = {
                'id': eventId,
                'keywords': [],
                'added': nnow,
            }
    eventItem['updated'] = nnow

    oldKeywords = set(eventItem['keywords'])
    oldKeywords.update(word['keywords'])
    eventItem['keywords'] = list(oldKeywords)

    words = eventItem.get('words', [])
    found = False
    for childWord in words:
        if childWord['page'].get('url') == word['page'].get('url'):
            found = True
            break
    if not found:
        words.insert(0, word)
    eventItem['words'] = words

    models.saveEvent(scope, eventItem)

def _archiveEvents(scope, events):
    _MIN_UPDATED_HOURS = 24
    startTime = dateutil.getHoursAs14(_MIN_UPDATED_HOURS)
    historEvents = models.getHistoryEvents(scope)
    if not historEvents:
        historEvents = {
            'items': [],
        }
    changed = False
    i = len(events['items']) - 1
    while i >= 0:
        if events['items'][i]['updated'] <= startTime:
            historEvents['items'].append(events['items'][i])
            del events['items'][i]
            changed = True
        i-= 1
    if changed:
        models.saveHistoryEvents(scope, historEvents)

def summarizeEvents(scope, *wordsList):
    events = models.getEvents(scope)
    if not events:
        events = {
            'counter': 0,
            'items': [],
        }

    _archiveEvents(scope, events)

    for event in events['items']:
        event['keywords'] = set(event['keywords'])

    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())
    for words in wordsList:
        # Identify less important words first,
        # so if multiple words map to the same event, the latter one win.
        words.sort(key=lambda word: word['pages'])

        for word in words:
            event = _summarizeEvent(scope, events, word, nnow)
            if event:
                _saveEventItem(scope, event['id'], word, nnow)

    for event in events['items']:
        event['keywords'] = list(event['keywords'])
    events['items'].sort(key=lambda item: item['word']['pages'], reverse=True)
    events['items'].sort(key=lambda item: item['updated'], reverse=True)
    models.saveEvents(scope, events)

def getEventPages(scope, since, size):
    events = models.getEvents(scope).get('items', [])
    count = 0
    result = []
    for event in events:
        event['word']['page']['event'] = {
                'id': event['id'],
                'keyword': ' '.join(event['word']['keywords']),
            }
        event['word']['page']['weight'] = event['word']['pages']
        result.append(event['word']['page'])
        count += 1
        if count >= size and event['updated'] < since:
            break
    return result

