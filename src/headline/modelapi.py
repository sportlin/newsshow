
import configmanager.models
from configmanager import cmapi

class LatestItem(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(LatestItem)

def _getKey():
    return 'Headlines'

def addItems(items):
    key = _getKey()
    latestItems = cmapi.getItemValue(key, [], modelname=LatestItem)
    for item in reversed(items):
        latestItems.insert(0, item)
    cmapi.saveItem(key, latestItems, modelname=LatestItem)

def getItems():
    return cmapi.getItemValue(_getKey(), [], modelname=LatestItem)

