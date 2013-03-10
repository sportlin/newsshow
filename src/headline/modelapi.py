import copy
import datetime
import logging

from commonutil import dateutil
import configmanager.models
from configmanager import cmapi
import globalconfig

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

def updateDatasources(source, items):
    datasources = getDatasources()

    #TODO: to be removed
    for i in range(len(datasources)):
        child = datasources[i]
        if 'source' not in child:
            pages = child['pages']
            del child['pages']
            datasources[i] = {
                    'source': child,
                    'pages': pages,
                }

    # clean old datasources
    days = globalconfig.getDatasourceDays()
    strStart = dateutil.getHoursAs14(days * 24)
    datasources = [child for child in datasources
                    if child['source']['added'] >= strStart]

    data = {
        'source': copy.deepcopy(source),
        'pages': copy.deepcopy(items),
    }

    found = None
    foundIndex = -1
    for i in range(len(datasources)):
        item = datasources[i]
        if item['source'].get('slug') == source.get('slug'):
            foundIndex = i
            found = item
            break
    if foundIndex >= 0:
        foundAdded = found['source'].get('added')
        dataAdded = source.get('added')
        if dataAdded is None or foundAdded is None \
                or dataAdded > foundAdded:
            datasources[foundIndex] = data
        elif dataAdded == foundAdded:
            found['pages'].extend(items)
            found['pages'].sort(key=lambda page: page.get('monitor') and
                                    page.get('monitor').get('rank'))
    else:
        datasources.append(data)
    key = _getDatasourcesKey()
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

def getTopicGroups(topicSlug):
    return cmapi.getItemValue('display.groups.' + topicSlug, [], modelname=DisplayItem)

def getDisplayTopic(topicSlug):
    foundTopic = None
    for topic in getDisplayTopics():
        if topic.get('slug') == topicSlug:
            foundTopic = topic
            break
    return foundTopic

def getDisplayDatasources():
    return cmapi.getItemValue('display.datasources', [], modelname=DisplayItem)

def saveDisplayDatasources(datasources):
    return cmapi.saveItem('display.datasources', datasources, modelname=DisplayItem)

def getDisplayDatasourceIds(onlyActive):
    items = cmapi.getItemValue('display.datasources', [], modelname=DisplayItem)
    result = {}
    for item in items:
        itemId = item.get('id')
        itemSlug = item.get('slug')
        if onlyActive and not item.get('active'):
            continue
        result[itemSlug] = itemId
    return result

def getDisplayDatasourceById(itemId):
    items = cmapi.getItemValue('display.datasources', [], modelname=DisplayItem)
    for item in items:
        if item.get('id') == itemId:
            return item
    return None

