from commonutil import dateutil
import configmanager.models
from configmanager import cmapi

import globalconfig
from headline import datareceiver

class LatestItem(configmanager.models.ConfigItem):
    pass

class DisplayItem(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(LatestItem)
cmapi.registerModel(DisplayItem)

def receiveData(datasource, items):
    if datasource.get('charts'):
        keyname = 'chartses'
    else:
        keyname = 'datasources'
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

def getDisplayTopics():
    return cmapi.getItemValue('display.topics', [], modelname=DisplayItem)

def getDisplayGroups():
    return cmapi.getItemValue('display.groups', [], modelname=DisplayItem)

def getTopicGroups(topicSlug):
    return cmapi.getItemValue('display.groups.' + topicSlug, [], modelname=DisplayItem)

def getDisplayTopic(topicSlug):
    foundTopic = None
    for topic in getDisplayTopics():
        if topic.get('slug') == topicSlug:
            foundTopic = topic
            break
    return foundTopic

def getDatasources():
    return cmapi.getItemValue('datasources', [], modelname=LatestItem)

def getChartses():
    return cmapi.getItemValue('chartses', [], modelname=LatestItem)

