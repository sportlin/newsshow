import copy
import datetime
import logging

from commonutil import stringutil
from commonutil import dateutil
import globalconfig
from . import modelapi

def saveItems(datasource, items):
    modelapi.updateDatasources(datasource, items)
    modelapi.saveDatasourceHistory(datasource, items)

def getDatasourceHistory():
    latestHours = globalconfig.getSiteLatestHours()
    startTime = datetime.datetime.utcnow() - datetime.timedelta(hours=latestHours)
    strstart = dateutil.getDateAs14(startTime)
    return [ item for item in modelapi.getDatasourceHistory()
                if item.get('added', '') >= strstart]

"""
Judge wether all criterions are matched.
"""
def _isTagsMatch(criterionTags, tags):
    matched = True
    for tag in criterionTags:
        if tag not in tags:
            matched = False
            break
    return matched

def _getDatasourcesByTags(datasources, tags):
    result = []
    for datasource in datasources:
        datasourceTags = datasource.get('tags', [])
        if not tags:
            continue
        if not _isTagsMatch(tags, datasourceTags):
            continue
        result.append(copy.deepcopy(datasource))
    return result

def _getUnmatchedDatasources(datasources, items):
    result = []
    for datasource in datasources:
        datasourceTags = datasource.get('tags', [])
        matched = False
        for item in items:
            tags = item.get('tags')
            if not tags:
                continue
            if _isTagsMatch(tags, datasourceTags):
                matched = True
                break
        if not matched:
            result.append(copy.deepcopy(datasource))
    if result:
        result = _sortDatasources(result, orderField='added', reverse=True)
    return result

def _sortDatasources(datasources, orderField='order', reverse=False):
    return sorted(datasources, key=lambda source:
                source.get(orderField) if source.get(orderField)
                else stringutil.getMaxOrder(), reverse=reverse)

# topic/group/source/page
def getTopics():
    datasources = modelapi.getDatasources()

    displayConfig = modelapi.getDisplayConfig()
    showUnknown = displayConfig.get('show.unknown', True)
    defaultGroups = displayConfig.get('groups')
    topics = displayConfig.get('topics', [])
    resultTopics = []
    for topic in topics:
        topicTags = topic.get('tags')
        if not topicTags:
            continue

        topicDatasources = _getDatasourcesByTags(datasources, topicTags)
        if not topicDatasources:
            continue
        groups = topic.get('groups')
        if groups is None:
            if defaultGroups:
                groups = defaultGroups
            else:
                groups = []
        topicGroups = []
        for group in groups:
            groupTags = group.get('tags')
            if not groupTags:
                continue
            groupDatasources = _getDatasourcesByTags(topicDatasources, groupTags)
            if not groupDatasources:
                continue
            topicGroup = {}
            topicGroup['slug'] = group.get('slug')
            topicGroup['name'] = group.get('name')
            topicGroup['datasources'] = _sortDatasources(groupDatasources)
            topicGroups.append(topicGroup)

        if showUnknown:
            unmatched = _getUnmatchedDatasources(topicDatasources, groups)
            if unmatched:
                unknownGroup = {
                    'slug': 'unknown',
                    'name': '',
                    'datasources': unmatched,
                }
                topicGroups.append(unknownGroup)
        resultTopic = {}
        resultTopic['slug'] = topic.get('slug')
        resultTopic['name'] = topic.get('name')
        resultTopic['groups'] = topicGroups
        resultTopics.append(resultTopic)

    if showUnknown:
        unmatched = _getUnmatchedDatasources(datasources, topics)
        if unmatched:
            unknownTopic = {
                'slug': 'unknown',
                'name': '',
                'groups': [
                    {
                        'slug': 'unknown',
                        'name': '',
                        'datasources': unmatched,
                    }
            ]}
            resultTopics.append(unknownTopic)
    return resultTopics

def cleanData():
    datasourceDays = globalconfig.getDatasourceDays()
    datasourceHistoryDays = globalconfig.getDatasourceHistoryDays()
    logging.info('Datasource days: %s.' % (datasourceDays, ))
    if datasourceDays > 0:
        modelapi.cleanDatasources(datasourceDays)
        logging.info('Datasource cleaned.')
    logging.info('Datasource history days: %s.' % (datasourceHistoryDays, ))
    if datasourceHistoryDays > 0:
        modelapi.cleanDatasourceHistory(datasourceHistoryDays)
        logging.info('Datasource history cleaned.')

