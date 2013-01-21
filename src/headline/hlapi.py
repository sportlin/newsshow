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

def _addTopicPages(topic, datasource, items):
    if isinstance(topic, basestring):
        topicSlug = topic
        topic = {}
    else:
        topicSlug = topic.get('slug')
        if topicSlug is None:
            topicSlug = ''
    historyHours = globalconfig.getTopicHistoryHours()
    savedTopic = modelapi.getTopicHistory(topicSlug)

    if topic:
        savedTopic['slug'] = topic.get('slug')
        savedTopic['name'] = topic.get('name')

    pages = savedTopic.get('pages')
    if pages is None:
        pages = []
        savedTopic['pages'] = pages

    for item in items:
        url = item.get('url')
        if not url:
            continue

        # remove old duplicated page
        for i in range(len(pages) -1, 0, -1):
            pageItem = pages[i]['page']
            if pageItem.get('url') == url:
                del pages[i]
                break

        # insert the latest page at top
        data = {
            'page': copy.deepcopy(item),
            'source': copy.deepcopy(datasource),
        }

        pages.insert(0, data)

    # clean old pages
    strStart = dateutil.getHoursAs14(historyHours)
    for i in range(len(pages) -1, 0, -1):
        pageSource = pages[i].get('source')
        if pageSource and pageSource.get('added') >= strStart:
            break
        del pages[i]

    savedTopic['pages'] = sorted(pages, key=lambda page:
                page.get('source').get('added'), reverse=True)

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
        _addTopicPages(topic, datasource, items)

def getTopicHistory(slug):
    if not slug:
        slug = _MOCK_ALL_TOPIC_SLUG
    return modelapi.getTopicHistory(slug)

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

def _getTopicWithGroups(topic, datasources, defaultGroups):
    topicTags = topic.get('tags')
    if not topicTags:
        return None
    topicDatasources = _getDatasourcesByTags(datasources, topicTags)
    if not topicDatasources:
        return None
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
    return resultTopic

# topic/group/source/page
def getTopics():
    datasources = modelapi.getDatasources()
    displayConfig = modelapi.getDisplayConfig()
    defaultGroups = displayConfig.get('groups')
    topics = displayConfig.get('topics', [])
    resultTopics = []
    for topic in topics:
        resultTopic = _getTopicWithGroups(topic, datasources, defaultGroups)
        if resultTopic:
            resultTopics.append(resultTopic)

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

def getTopicConfig():
    displayConfig = modelapi.getDisplayConfig()
    return displayConfig.get('topics', [])

def getTopic(topicSlug):
    displayConfig = modelapi.getDisplayConfig()
    topics = displayConfig.get('topics', [])
    foundTopic = None
    for topic in topics:
        if topic.get('slug') == topicSlug:
            foundTopic = topic
            break
    if not foundTopic:
        return None
    datasources = modelapi.getDatasources()
    defaultGroups = displayConfig.get('groups')
    resultTopic = _getTopicWithGroups(topic, datasources, defaultGroups)
    if not resultTopic:
        return None
    topicHistory = modelapi.getTopicHistory(topicSlug)
    if topicHistory:
        latestCount = globalconfig.getTopicHomeLatest()
        resultTopic['latest'] = topicHistory.get('pages')[:latestCount]
    return resultTopic

def _getPagesByTags(pages, tags):
    result = []
    for page in pages:
        pageTags = page.get('source').get('tags', [])
        if not _isTagsMatch(tags, pageTags):
            continue
        result.append(copy.deepcopy(page))
    return result

def getHomeData():
    topicHistory = modelapi.getTopicHistory(_MOCK_ALL_TOPIC_SLUG)
    latestCount = globalconfig.getTopicHomeLatest()
    displayConfig = modelapi.getDisplayConfig()
    topics = displayConfig.get('topics', [])
    pages = topicHistory.get('pages')
    resultTopics = []
    logging.info('pages: %s.' % (pages, ))
    for topic in topics:
        topicTags = topic.get('tags')
        if not topicTags:
            continue
        topicPages = _getPagesByTags(pages, topicTags)
        logging.info('topic: %s, pages: %s.' % (topic, topicPages, ))
        if not topicPages:
            continue
        topicSlug = topic.get('slug')
        resultTopic = {}
        resultTopic['slug'] = topicSlug
        resultTopic['name'] = topic.get('name')
        resultTopic['pages'] = topicPages[:latestCount]
        resultTopics.append(resultTopic)
    return {
        'topics': resultTopics,
        'latest': pages[:latestCount],
    }

