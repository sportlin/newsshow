import datetime

from commonutil import dateutil, stringutil
from searchengine import gnews, twitter

import globalutil
from . import models

def _isKeywordsGroupMatched(keywordsSet, keywordsGroup):
    matchedSize = 2
    for item in keywordsGroup:
        if len(set(item).intersection(keywordsSet)) >= matchedSize:
            return True
    return False

def updateKeywordsGroup(keywords, keywordsGroup):
    found = False
    keywordsSet = set(keywords)

    for item in keywordsGroup:
        if len(item) != len(keywords):
            continue
        if len(set(item).difference(keywordsSet)) == 0:
            found = True
            break
    if not found:
        keywordsGroup.insert(0, keywords)

def _summarizeEvent(exposePages, scope, events, word, nnow):
    createMinSize = 2
    if len(word['keywords']) < createMinSize:
        return None
    keywordsSet = set(word['keywords'])

    matchedEvent = None
    for event in events['items']:
        if _isKeywordsGroupMatched(word['keywords'], event['keywordsgroup']):
            matchedEvent = event
            break

    if not matchedEvent:
        events['counter'] += 1
        matchedEvent = {}
        matchedEvent['id'] = events['counter']
        matchedEvent['added'] = nnow
        matchedEvent['keywordsgroup'] = []

        events['items'].append(matchedEvent)
    if not matchedEvent.get('exposed'):
        matchedEvent['exposed'] = word['size'] >= exposePages
    matchedEvent['updated'] = nnow

    updateKeywordsGroup(word['keywords'], matchedEvent['keywordsgroup'])

    matchedEvent['word'] = word

    return matchedEvent

def _addMatcheds(eventPages, word, matcheds):
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
    return changed

def _addTwitterPage(eventPages, word, twitterAccount):
    if not twitterAccount:
        return
    keyword = ' '.join(word['keywords'][:2])
    tpages = twitter.search(keyword, twitterAccount)
    if not tpages:
        return False
    tpage = tpages[0]
    tpage['hash'] = stringutil.calculateHash([tpage['content']])
    existed = False
    for page in eventPages:
        if page.get('hash') == tpage['hash']:
            existed = True
            break
    if not existed:
        eventPages.append(tpage)
        return True
    return False

def _saveEventItem(scope, eventId, word, nnow, matcheds, twitterAccount):
    eventItem = models.getEvent(scope, eventId)
    if not eventItem:
        eventItem = {
                'id': eventId,
                'keywords': [],
                'added': nnow,
            }
    eventItem['updated'] = nnow

    eventPages = eventItem.get('pages', [])
    changed = False
    if _addMatcheds(eventPages, word, matcheds):
        changed = True
    if _addTwitterPage(eventPages, word, twitterAccount):
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

def summarizeEvents(eventCriterion, scope, words, pages, twitterAccount):
    exposePages = eventCriterion['expose.pages']
    events = models.getEvents(scope)
    if not events:
        events = {
            'counter': 0,
            'items': [],
        }

    _archiveEvents(scope, events)

    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())

    for keywords in reversed(words):
        matcheds = globalutil.search(pages, keywords)
        if not matcheds:
            continue
        word = {}
        word['keywords'] = keywords
        word['size'] = len(matcheds)
        word['page'] = matcheds[0]
        event = _summarizeEvent(exposePages, scope, events, word, nnow)
        if event:
            _saveEventItem(scope, event['id'], word, nnow, matcheds, twitterAccount)

    events['items'].sort(key=lambda item: item['updated'], reverse=True)
    events['items'].sort(key=lambda item: item['word']['size'], reverse=True)
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
                'keyword': ', '.join(event['word']['keywords'][:3]),
                'exposed': event['exposed'],
            }
        event['word']['page']['weight'] = event['word']['size']
        result.append(event['word']['page'])
        count += 1
    return result

