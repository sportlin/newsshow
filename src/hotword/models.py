
import configmanager.models
from configmanager import cmapi

class HotWord(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(HotWord)

def saveWords(value):
    cmapi.saveItem('now', value, modelname=HotWord)

def getWords():
    return cmapi.getItemValue('now', {}, modelname=HotWord)

