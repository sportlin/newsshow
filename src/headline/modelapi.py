import copy
import datetime
import logging

from commonutil import dateutil
import configmanager.models
from configmanager import cmapi

class LatestItem(configmanager.models.ConfigItem):
    pass

class TopicHistory(configmanager.models.ConfigItem):
    pass

class DisplayItem(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(LatestItem)
cmapi.registerModel(TopicHistory)
cmapi.registerModel(DisplayItem)

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
    found = None
    foundIndex = -1
    for i in range(len(datasources)):
        item = datasources[i]
        if item.get('slug') == datasource.get('slug'):
            foundIndex = i
            found = item
            break
    if foundIndex >= 0:
        foundCounter = found.get('counter')
        dataCounter = datasource.get('counter')
        if dataCounter is None or foundCounter is None\
                or dataCounter > foundCounter:
            datasources[foundIndex] = data
        elif dataCounter == foundCounter:
            found['pages'].extend(items)
    else:
        datasources.append(data)
    cmapi.saveItem(key, datasources, modelname=LatestItem)

def _getTopicHistoryKey(topicSlug):
    return topicSlug

def getTopicHistory(topicSlug):
    key = _getTopicHistoryKey(topicSlug)
    items = cmapi.getItemValue(key, {}, modelname=TopicHistory)
    return items

def saveTopicHistory(topicSlug, value):
    key = _getTopicHistoryKey(topicSlug)
    cmapi.saveItem(key, value, modelname=TopicHistory)

def getDisplayTopics():
    return cmapi.getItemValue('display.topics', [], modelname=DisplayItem)

def getDisplayGroups():
    return cmapi.getItemValue('display.groups', [], modelname=DisplayItem)

def getDisplayTopic(topicSlug):
    foundTopic = None
    for topic in getDisplayTopics():
        if topic.get('slug') == topicSlug:
            foundTopic = topic
            break
    return foundTopic

