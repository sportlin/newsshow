import copy
import logging

from commonutil import stringutil
from . import modelapi

def saveItems(datasource, items):
    modelapi.updateDatasources(datasource, items)
    modelapi.saveItems(datasource, items)

def getItems():
    return modelapi.getItems()

# topic/group/source/page
def getTopics():
    displayConfig = modelapi.getDisplayConfig()
    topicConfigs = displayConfig.get('topic', {})
    groupConfigs = displayConfig.get('group', {})
    sourceConfigs = displayConfig.get('source', {})

    datasources = modelapi.getDatasources().values()

    # populate attr (topicorder/topic/grouporder/group/sourceorder) for datasoure
    for datasource in datasources:
        topicSlug = datasource.get('source').get('topic')
        sourceSlug = datasource.get('source').get('slug')

        topicConfig = topicConfigs.get(topicSlug)
        datasource['topic'] = datasource.get('source').get('topic')
        if topicSlug and topicConfig:
            datasource['topicorder'] = topicConfig.get('order')
        else:
            datasource['topicorder'] = stringutil.getMaxOrder()

        # process source first, then datasource has group attr
        sourceconfig = sourceConfigs.get(sourceSlug)
        if sourceconfig:
            sourcegroup = sourceconfig.get('group')
            if sourcegroup:
                datasource['group'] = sourcegroup
            sourceorder = sourceconfig.get('order')
            if sourceorder:
                datasource['group'] = sourceorder
        if not datasource.get('sourceorder'):
            datasource['sourceorder'] = stringutil.getMaxOrder()

        groupSlug = datasource.get('group')
        groupConfig = groupConfigs.get(groupSlug)
        if groupSlug and groupConfig:
            datasource['grouporder'] = groupConfig.get('order')
        else:
            datasource['grouporder'] = stringutil.getMaxOrder()

    datasources = sorted(datasources, key=lambda datasource:
                            datasource.get('sourceorder'))
    datasources = sorted(datasources, key=lambda datasource:
                            datasource.get('group'))
    datasources = sorted(datasources, key=lambda datasource:
                            datasource.get('grouporder'))
    datasources = sorted(datasources, key=lambda datasource:
                            datasource.get('topic'))
    datasources = sorted(datasources, key=lambda datasource:
                            datasource.get('topicorder'))

    lastTopic = None
    lastGroup = None
    topics = []
    for datasource in datasources:
        topicSlug = datasource.get('source').get('topic')
        if not lastTopic or topicSlug != lastTopic['slug']:
            topicConfig = topicConfigs.get(topicSlug)
            if topicConfig:
                lastTopic = copy.deepcopy(topicConfig)
            else:
                lastTopic = {}
            lastTopic['slug'] = topicSlug
            lastTopic['groups'] = []
            topics.append(lastTopic)

            lastGroup = None

        groupSlug = datasource.get('group')
        if not lastGroup or groupSlug != lastGroup['slug']:
            groupConfig = groupConfigs.get(groupSlug)
            if groupConfig:
                lastGroup = copy.deepcopy(groupConfig)
            else:
                lastGroup = {}
            lastGroup['slug'] = groupSlug
            lastGroup['sources'] = []
            lastTopic['groups'].append(lastGroup)
        source = copy.deepcopy(datasource.get('source'))
        source['pages'] = datasource['pages']
        lastGroup['sources'].append(source)

    return topics

