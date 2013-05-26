import datetime

from commonutil import dateutil
import globalutil
from . import models

def _isListIntersection(list1, list2):
    for item in list1:
        if item in list2:
            return True
    return False

def _summarizeEvent(exposePages, scope, events, word, nnow):
    createMinSize = 2
    if len(word['keywords']) < createMinSize:
        return None

    matchedEvent = None
    latestKeywordsCount = 10
    for event in events['items']:
        if _isListIntersection(word['keywords'], event['keywords'][:latestKeywordsCount]):
            matchedEvent = event
            break

    if not matchedEvent:
        events['counter'] += 1
        matchedEvent = {}
        matchedEvent['id'] = events['counter']
        matchedEvent['added'] = nnow
        matchedEvent['keywords'] = []

        events['items'].append(matchedEvent)
    if not matchedEvent.get('exposed'):
        matchedEvent['exposed'] = word['weight'] >= exposePages
    matchedEvent['updated'] = nnow
    for keyword in reversed(word['keywords']):
        if keyword in matchedEvent['keywords']:
            matchedEvent['keywords'].remove(keyword)
        matchedEvent['keywords'].insert(0, keyword)
    matchedEvent['word'] = word

    return matchedEvent

def _saveEventItem(scope, eventId, word, nnow, pages):
    eventItem = models.getEvent(scope, eventId)
    if not eventItem:
        eventItem = {
                'id': eventId,
                'keywords': [],
                'added': nnow,
            }
    eventItem['updated'] = nnow

    matcheds = globalutil.search(pages, word['keywords'])
    eventPages = eventItem.get('pages', [])
    changed = False
    for matched in matcheds:
        found = False
        for eventPage in eventPages:
            if eventPage.get('url') == matched.get('url'):
                found = True
                break
        if not found:
            matched['keywords'] = word['keywords']
            eventPages.append(matched)
            changed = True
    eventItem['pages'] = eventPages

    for keyword in reversed(word['keywords']):
        if keyword not in eventItem['keywords']:
            eventItem['keywords'].insert(0, keyword)
    if changed:
        models.saveEvent(scope, eventItem)

def _archiveEvents(scope, events):
    _MIN_UPDATED_HOURS = 24
    _MIN_DDED_HOURS = 24
    startTime = dateutil.getHoursAs14(_MIN_UPDATED_HOURS)
    addedStartTime = dateutil.getHoursAs14(_MIN_DDED_HOURS)
    historEvents = models.getHistoryEvents(scope)
    if not historEvents:
        historEvents = {
            'items': [],
        }
    changed = False
    i = len(events['items']) - 1
    while i >= 0:
        if events['items'][i]['updated'] <= startTime or events['items'][i]['added'] <= startTime:
            if events['items'][i]['exposed']:
                historEvents['items'].append(events['items'][i])
                changed = True
            else:
                models.removeEvent(scope, events['items'][i]['id'])
            del events['items'][i]
        i-= 1
    if changed:
        models.saveHistoryEvents(scope, historEvents)

def summarizeEvents(eventCriterion, scope, words, pages):
    exposePages = eventCriterion['expose.pages']
    events = models.getEvents(scope)
    if not events:
        events = {
            'counter': 0,
            'items': [],
        }

    _archiveEvents(scope, events)

    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())
    # Identify less important words first,
    # so if multiple words map to the same event, the latter one win.
    words.sort(key=lambda word: word['weight'])

    for word in words:
        if 'page' not in word:
            continue
        event = _summarizeEvent(exposePages, scope, events, word, nnow)
        if event:
            _saveEventItem(scope, event['id'], word, nnow, pages)

    events['items'].sort(key=lambda item: item['updated'], reverse=True)
    events['items'].sort(key=lambda item: item['word']['weight'], reverse=True)
    events['updated'] = nnow
    models.saveEvents(scope, events)

def getEventPages(scope):
    eventsData = models.getEvents(scope)
    events = eventsData.get('items', [])
    count = 0
    result = []
    urls = set()
    for event in events:
        if event['updated'] != eventsData['updated']:
            continue
        url = event['word']['page'].get('url')
        if url in urls:
            continue
        urls.add(url)
        event['word']['page']['event'] = {
                'id': event['id'],
                'keyword': ', '.join(event['word']['keywords']),
                'exposed': event['exposed'],
            }
        event['word']['page']['weight'] = event['word']['weight']
        result.append(event['word']['page'])
        count += 1
    return result

