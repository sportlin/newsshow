import copy

import configmanager.models
from configmanager import cmapi

class LatestItem(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(LatestItem)

def getDisplayConfig():
    return cmapi.getItemValue('display.structure', {})

def _getItemsKey():
    return 'datasource.history'

def getDatasourceHistory():
    items = cmapi.getItemValue(_getItemsKey(), [], modelname=LatestItem)
    return items

def saveDatasourceHistory(datasource, items):
    data = copy.deepcopy(datasource)
    data['pages'] = copy.deepcopy(items)

    key = _getItemsKey()
    latestItems = getItems()
    latestItems.insert(0, data)
    cmapi.saveItem(key, latestItems, modelname=LatestItem)

def _getDatasourcesKey():
    return 'datasources'

def getDatasources():
    key = _getDatasourcesKey()
    datasources = cmapi.getItemValue(key, [], modelname=LatestItem)
    return datasources

def updateDatasources(datasource, items):
    data = copy.deepcopy(datasource)
    data['pages'] = copy.deepcopy(items)

    sourceSlug = datasource.get('slug')
    key = _getDatasourcesKey()
    datasources = getDatasources()
    found = -1
    for i in range(len(datasources)):
        item = datasources[i]
        if item.get('slug') == datasource.get('slug'):
            found = i
            break
    if found >= 0:
        datasources[found] = data
    else:
        datasources.append(data)
    cmapi.saveItem(key, datasources, modelname=LatestItem)

