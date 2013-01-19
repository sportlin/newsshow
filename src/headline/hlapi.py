import copy
import datetime
import logging

from commonutil import stringutil
from commonutil import dateutil
import globalconfig
from . import modelapi

_MOCK_ALL_TOPIC_SLUG = 'all'

def saveItems(datasource, items):
    displayConfig = modelapi.getDisplayConfig()
    topics = displayConfig.get('topics', [])
    modelapi.updateDatasources(datasource, items)
    _addTopicPages(_MOCK_ALL_TOPIC_SLUG, datasource, items)
    _addTopicsPages(topics, datasource, items)

def _addTopicPages(topicSlug, datasource, items):
    historyHours = globalconfig.getTopicHistoryHours()
    savedTopic = modelapi.getTopicHistory(topicSlug)

    pages = savedTopic.get('pages')
    if pages is None:
        pages = []
        savedTopic['pages'] = pages

    # clean old pages
    strStart = dateutil.getHoursAs14(historyHours)
    for i in range(len(pages)):
        pageSource = pages[i].get('source')
        if not pageSource or pageSource.get('added') < strStart:
            del pages[i]

    for item in items:
        url = item.get('url')
        if not url:
            continue

        # remove old duplicated page
        foundIndex = -1
        for i in range(len(pages)):
            page = pages[i]
            if page.get('url') == url:
                foundIndex = i
                break
        if foundIndex >= 0:
            del pages[foundIndex]

        # insert the latest page at top
        data = {
            'page': copy.deepcopy(item),
            'source': copy.deepcopy(datasource),
        }
        pages.insert(0, data)

    modelapi.saveTopicHistory(topicSlug, savedTopic)

def _addTopicsPages(topics, datasource, items):
    datasourceTags = datasource.get('tags', [])
    for topic in topics:
        topicSlug = topic.get('slug')
        if not topicSlug:
            continue
        topicTags = topic.get('tags')
        if not topicTags:
            continue
        if not _isTagsMatch(topicTags, datasourceTags):
            continue
        _addTopicPages(topicSlug, datasource, items)

def getPageHistory():
    topic = modelapi.getTopicHistory(_MOCK_ALL_TOPIC_SLUG)
    if not topic:
        return []
    pages = topic.get('pages')
    if pages is None:
        return []
    return pages

def getDatasources():
    datasources = modelapi.getDatasources()
    datasources = sorted(datasources, key=lambda datasource: datasource.get('added'), reverse=True)
    return datasources

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
            topicGroup['datasources'] = _sortDatasources(groupDatasources,
                                            orderField='added', reverse=True)
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

