
import configmanager.models
from configmanager import cmapi

class HotEvents(configmanager.models.ConfigItem):
    pass

class HotEvent(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(HotEvents)
cmapi.registerModel(HotEvent)

def saveEvents(scope, value):
    cmapi.saveItem(scope, value, modelname=HotEvents)

def getEvents(scope):
    return cmapi.getItemValue(scope, {}, modelname=HotEvents)

def saveEvent(scope, event):
    cmapi.saveItem(scope + '.' + str(event['id']), event, modelname=HotEvent)

def removeEvent(scope, eventId):
    cmapi.removeItem(scope + '.' + str(eventId), modelname=HotEvent)

def getEvent(scope, eventId):
    return cmapi.getItemValue(scope + '.' + str(eventId), {}, modelname=HotEvent)

def saveHistoryEvents(scope, value):
    cmapi.saveItem(scope + '.history', value, modelname=HotEvents)

def getHistoryEvents(scope):
    return cmapi.getItemValue(scope + '.history', {}, modelname=HotEvents)

def cleanData(scope):
    events = getEvents(scope)

    eventsH = getHistoryEvents(scope)
    for event in events.get('items', []) + eventsH.get('items', []):
        eventItem = getEvent(scope, event['id'])
        if not eventItem:
            continue
        if 'words' not in eventItem:
            continue
        words = eventItem.get('words', [])
        pages = eventItem.get('pages', [])
        for childWord in words:
            pages.append(childWord['page'])
        del eventItem['words']
        eventItem['pages'] = pages
        saveEvent(scope, eventItem)

