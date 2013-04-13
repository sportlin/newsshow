
import configmanager.models
from configmanager import cmapi

class HotEvent(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(HotEvent)

def saveEvents(scope, value):
    cmapi.saveItem(scope + '.ids', value, modelname=HotEvent)

def getEvents(scope):
    return cmapi.getItemValue(scope + '.ids', {}, modelname=HotEvent)

def saveEvent(scope, event):
    cmapi.saveItem(scope + '.' + str(event['id']), event, modelname=HotEvent)

def getEvent(scope, eventId):
    return cmapi.getItemValue(scope + '.' + str(eventId), {}, modelname=HotEvent)

