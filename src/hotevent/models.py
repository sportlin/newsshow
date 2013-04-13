
import configmanager.models
from configmanager import cmapi

class HotEvent(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(HotEvent)

def saveEvents(scope, value):
    cmapi.saveItem(scope + '.ids', value, modelname=HotEvent)

def getEvents(scope):
    return cmapi.getItemValue(scope + '.ids', {}, modelname=HotEvent)

