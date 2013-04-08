
import configmanager.models
from configmanager import cmapi

class HotWord(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(HotWord)

def saveWords(keyname, value):
    cmapi.saveItem(keyname, value, modelname=HotWord)

def getWords(keyname):
    return cmapi.getItemValue(keyname, {}, modelname=HotWord)

