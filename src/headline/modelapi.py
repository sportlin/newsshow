import copy

import configmanager.models
from configmanager import cmapi

class LatestItem(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(LatestItem)

def _getItemsKey():
    return 'Headlines'

def getItems():
    return cmapi.getItemValue(_getItemsKey(), [], modelname=LatestItem)

def saveItems(datasource, items):
    key = _getItemsKey()
    latestItems = getItems()
    for item in reversed(items):
        copyitem = copy.deepcopy(item)
        copyitem['source'] = copy.deepcopy(datasource)
        latestItems.insert(0, copyitem)
    cmapi.saveItem(key, latestItems, modelname=LatestItem)

def _getDatasourcesKey():
    return 'Datasources'

def getDatasources():
    key = _getDatasourcesKey()
    return cmapi.getItemValue(key, {}, modelname=LatestItem)

def updateDatasources(datasource, items):
    sourceSlug = datasource.get('slug')
    key = _getDatasourcesKey()
    datasources = getDatasources()
    value = {'source': datasource, 'items': items}
    datasources[sourceSlug] = value
    cmapi.saveItem(key, datasources, modelname=LatestItem)

