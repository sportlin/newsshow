import copy
import datetime
import logging

from commonutil import stringutil
from commonutil import dateutil
import globalconfig
from . import modelapi

def saveItems(datasource, items):
    topics = modelapi.getDisplayTopics()
    modelapi.updateDatasources(datasource, items)
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

    pages = savedTopic.get('pages')
    if pages is None:
        pages = []
        savedTopic['pages'] = pages

    for item in items:
        monitorPage = item.get('monitor')
        if not monitorPage:
            continue
        url = monitorPage.get('url')
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

def _getTopicGroups(topic, datasources, defaultGroups):
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

    return topicGroups

# topic/group/source/page
def getTopics():
    datasources = modelapi.getDatasources()
    defaultGroups = modelapi.getDisplayGroups()
    topics = modelapi.getDisplayTopics()
    resultTopics = []
    for topic in topics:
        topicGroups = _getTopicGroups(topic, datasources, defaultGroups)
        if topicGroups:
            resultTopic = copy.deepcopy(topic.get('ui'))
            resultTopic['groups'] = topicGroups
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

def getTopicsConfig():
    return [topic.get('ui') for topic in modelapi.getDisplayTopics()]

def _populateDatasourceId(datasourceIds, datasources):
    for datasource in datasources:
        datasourceId = datasourceIds.get(datasource.get('slug'))
        if datasourceId:
            datasource['id'] = datasourceId

def getTopic(topicSlug):
    topics = modelapi.getDisplayTopics()
    foundTopic = modelapi.getDisplayTopic(topicSlug)
    if not foundTopic:
        return None
    datasources = modelapi.getDatasources()
    defaultGroups = modelapi.getDisplayGroups()
    topicGroups = _getTopicGroups(foundTopic, datasources, defaultGroups)
    resultTopic = None
    if topicGroups:
        # populate datasource id for datasources, as exposed id.
        datasourceIds = modelapi.getDisplayDatasourceIds(onlyActive=True)
        for topicGroup in topicGroups:
            _populateDatasourceId(datasourceIds, topicGroup['datasources'])
        resultTopic = copy.deepcopy(foundTopic.get('ui'))
        resultTopic['groups'] = topicGroups
    return resultTopic

def getTopicHistory(slug):
    foundTopic = modelapi.getDisplayTopic(slug)
    if not foundTopic:
        return None
    topicHistory = modelapi.getTopicHistory(slug)
    resultTopic = copy.deepcopy(foundTopic.get('ui'))
    if topicHistory:
        resultTopic['pages'] = topicHistory['pages']
    return resultTopic

def getTopicPicture(slug):
    foundTopic = modelapi.getDisplayTopic(slug)
    if not foundTopic:
        return None
    topicHistory = modelapi.getTopicHistory(slug)
    resultTopic = copy.deepcopy(foundTopic.get('ui'))
    if topicHistory:
        resultTopic['pages'] = [ page for page in topicHistory['pages']
                                    if page['page'].get('editor') and
                                        page['page'].get('editor').get('img') ]
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
    datasources = modelapi.getDatasources()
    pages = []
    for datasource in datasources:
        dpages = datasource['pages']
        del datasource['pages']
        for page in dpages:
            page['source'] = datasource
        pages.extend(dpages)
    pages.sort(key=lambda page: page['source']['added'], reverse=True)
    latestCount = globalconfig.getTopicHomeLatest()
    topics = modelapi.getDisplayTopics()
    resultTopics = []
    for topic in topics:
        topicTags = topic.get('tags')
        if not topicTags:
            continue
        topicPages = _getPagesByTags(pages, topicTags)
        if not topicPages:
            continue
        resultTopic = copy.deepcopy(topic.get('ui'))
        resultTopic['pages'] = topicPages[:latestCount]
        resultTopics.append(resultTopic)
    return {
        'topics': resultTopics,
    }

def getDatasourceHistory(sourceId):
    datasource = modelapi.getDisplayDatasourceById(sourceId)
    if not datasource:
        return None
    topicSlug = datasource.get('topic')
    sourceSlug = datasource.get('slug')
    topicHistory = modelapi.getTopicHistory(topicSlug)
    foundTopic = modelapi.getDisplayTopic(topicSlug)
    if topicHistory:
        pages = topicHistory['pages']
        pages = [page for page in pages
                    if page['source'].get('slug') == sourceSlug]
        if pages:
            datasource['name'] = pages[0]['source']['name']
        datasource['pages'] =  [page['page'] for page in pages]
    if foundTopic:
        datasource['topicName'] = foundTopic['ui']['name']
    return datasource

def getDisplayDatasources():
    datasources = modelapi.getDisplayDatasources()
    return [datasource for datasource in datasources]

def getUnexposedDatasources():
    datasources = modelapi.getDatasources()
    topics = modelapi.getDisplayTopics()
    result = []
    datasourceIds = modelapi.getDisplayDatasourceIds(onlyActive=False)
    for topic in topics:
        topicTags = topic.get('tags')
        if not topicTags:
            return None
        topicDatasources = _getDatasourcesByTags(datasources, topicTags)
        for datasource in topicDatasources:
            if datasource.get('slug') in datasourceIds:
                continue
            suggestId = ''
            parts = datasource['slug'].split('.')
            if len(parts) > 1:
                suggestId = parts[1]
            result.append({
                'slug': datasource['slug'],
                'name': datasource['name'],
                'topic': topic['slug'],
                'id': suggestId,
            })
    return result

def exposeDatasource(topic, slug, sourceId):
    datasources = modelapi.getDisplayDatasources()
    # id can not be duplicated.
    for datasource in datasources:
        if datasource['id'] == sourceId and slug and datasource['slug'] != slug:
            return
    found = None
    for datasource in datasources:
        if datasource['id'] == sourceId:
            found = datasource
            break
    if not found:
        found = {}
        datasources.append(found)
    if topic:
        found['topic'] = topic
    if slug:
        found['slug'] = slug
    if sourceId:
        found['id'] = sourceId
    found['active'] = True
    datasources.sort(key=lambda datasource: datasource.get('topic'))
    datasources.sort(key=lambda datasource: datasource.get('active'))
    modelapi.saveDisplayDatasources(datasources)

def closeDatasource(sourceId):
    datasources = modelapi.getDisplayDatasources()
    found = None
    for datasource in datasources:
        if datasource['id'] == sourceId:
            found = datasource
            break
    if found:
        found['active'] = False
        modelapi.saveDisplayDatasources(datasources)

