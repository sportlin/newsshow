from commonutil import dateutil
import configmanager.models
from configmanager import cmapi

import globalconfig
from headline import datareceiver

class LatestItem(configmanager.models.ConfigItem):
    pass

class ChannelGroup(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(LatestItem)
cmapi.registerModel(ChannelGroup)


def getChannelGroups(slug):
    result = cmapi.getItemValue(slug, [], modelname=ChannelGroup)
    if not result:
        result = cmapi.getItemValue('default', [], modelname=ChannelGroup)
    return result

def receiveData(datasource, items):
    if datasource.get('charts'):
        keyname = 'chartses'
    else:
        keyname = 'sites'
    _saveDatasource(datasource, items, keyname)

class DataReceiver(datareceiver.BasicDataReceiver):

    def __init__(self, name):
        datareceiver.BasicDataReceiver.__init__(self, name)

    def onData(self, datasource, items):
        receiveData(datasource, items)

datareceiver.registerReceiver(DataReceiver('Source Now Receiver'))

def _saveDatasource(datasource, items, keyname):
    datasources = cmapi.getItemValue(keyname, [], modelname=LatestItem)

    days = globalconfig.getDatasourceDays()
    strStart = dateutil.getHoursAs14(days * 24)
    datasources = [child for child in datasources
                    if child['source']['added'] >= strStart]

    data = {
        'source': datasource,
        'pages': items,
    }

    foundIndex = -1
    for i in range(len(datasources)):
        item = datasources[i]
        if item['source'].get('slug') == datasource.get('slug'):
            foundIndex = i
            break
    if foundIndex >= 0:
        datasources[foundIndex] = data
    else:
        datasources.append(data)
    cmapi.saveItem(keyname, datasources, modelname=LatestItem)

def cleanData():
    pass

def getDatasources(keyname=None):
    if not keyname:
        keyname = 'sites'
    return cmapi.getItemValue(keyname, [], modelname=LatestItem)

def getPages(datasources=None, keyname=None):
    if keyname:
        datasources = cmapi.getItemValue(keyname, [], modelname=LatestItem)
    pages = []
    for datasource in datasources:
        for childPage in datasource['pages']:
            childPage['source'] = datasource['source']
            pages.append(childPage)
    return pages

