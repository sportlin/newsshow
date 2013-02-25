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
        for i in range(len(pages) - 1, -1, -1):
            pageItem = pages[i]['page']
            if pageItem.get('monitor').get('url') == url:
                del pages[i]

        # insert the latest page at top
        data = {
            'page': copy.deepcopy(item),
            'source': copy.deepcopy(datasource),
        }

        pages.insert(0, data)

    # clean old pages
    strStart = dateutil.getHoursAs14(historyHours)
    for i in range(len(pages) - 1, -1, -1):
        pageSource = pages[i].get('source')
        if not pageSource or pageSource.get('added') < strStart:
            del pages[i]

    savedTopic['pages'] = sorted(pages, key=lambda page:
                page.get('page').get('monitor').get('published') or
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
        datasourceTags = datasource.get('source').get('tags', [])
        if not tags:
            continue
        if not _isTagsMatch(tags, datasourceTags):
            continue
        result.append(datasource)
    return result

def _getUnmatchedDatasources(datasources, items):
    result = []
    for datasource in datasources:
        datasourceTags = datasource.get('source').get('tags', [])
        matched = False
        for item in items:
            tags = item.get('tags')
            if not tags:
                continue
            if _isTagsMatch(tags, datasourceTags):
                matched = True
                break
        if not matched:
            result.append(datasource)
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
            resultTopic = topic.get('ui')
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
    datasourceIds = modelapi.getDisplayDatasourceIds(onlyActive=True)
    for topic in resultTopics:
        # populate datasource id for datasources, as exposed id.
        topicGroups = topic.get('groups')
        for topicGroup in topicGroups:
            _prepareDatasource4Show(datasourceIds, topicGroup['datasources'])

    return resultTopics

def getTopicsConfig():
    return [topic.get('ui') for topic in modelapi.getDisplayTopics()]

def _prepareDatasource4Show(datasourceIds, datasources):
    for datasource in datasources:
        datasourceId = datasourceIds.get(datasource['source'].get('slug'))
        if datasourceId:
            datasource['source']['id'] = datasourceId
        pages = datasource['pages']
        if pages:
            datasource['pages'] = [ page['monitor'] for page in pages ]

def getTopic(topicSlug):
    foundTopic = modelapi.getDisplayTopic(topicSlug)
    if not foundTopic:
        return None
    datasources = modelapi.getDatasources()
    defaultGroups = modelapi.getDisplayGroups()
    resultTopic = resultTopic = foundTopic.get('ui')
    topicGroups = _getTopicGroups(foundTopic, datasources, defaultGroups)
    if topicGroups:
        # populate datasource id for datasources, as exposed id.
        datasourceIds = modelapi.getDisplayDatasourceIds(onlyActive=True)
        for topicGroup in topicGroups:
            _prepareDatasource4Show(datasourceIds, topicGroup['datasources'])
        resultTopic['groups'] = topicGroups
    return resultTopic

def getTopicHistory(slug):
    foundTopic = modelapi.getDisplayTopic(slug)
    if not foundTopic:
        return None
    topicHistory = modelapi.getTopicHistory(slug)
    resultTopic = foundTopic.get('ui')
    if topicHistory:
        pages = []
        for child in topicHistory['pages']:
            monitorPage = child['page'].get('monitor')
            editorPage = child['page'].get('editor')
            if editorPage:
                editorPage['source'] = child['source']
                if monitorPage:
                    if 'keyword' in monitorPage:
                        editorPage['keyword'] = monitorPage['keyword']
                    if 'rank' in monitorPage:
                        editorPage['rank'] = monitorPage['rank']
                pages.append(editorPage)
        resultTopic['pages'] = pages
    return resultTopic

def getTopicPicture(slug):
    foundTopic = modelapi.getDisplayTopic(slug)
    if not foundTopic:
        return None
    topicHistory = modelapi.getTopicHistory(slug)
    resultTopic = foundTopic.get('ui')
    pages = []
    if topicHistory:
        for child in topicHistory['pages']:
            monitorPage = child['page'].get('monitor')
            if monitorPage and 'img' in monitorPage:
                pages.append(monitorPage)
            else:
                editorPage = child['page'].get('editor')
                if editorPage and 'img' in editorPage:
                    pages.append(editorPage)
    resultTopic['pages'] = pages
    return resultTopic

def _getPagesByTags(pages, tags):
    result = []
    for page in pages:
        pageTags = page.get('source').get('tags', [])
        if not _isTagsMatch(tags, pageTags):
            continue
        result.append(page)
    return result

def getHomeData():
    datasources = modelapi.getDatasources()
    pages = []
    for datasource in datasources:
        for childPage in datasource['pages']:
            monitorPage = childPage.get('monitor')
            if not monitorPage or not monitorPage.get('url'):
                continue
            if datasource['source'].get('charts') and not monitorPage.get('published'):
                continue
            if 'title' in monitorPage:
                page = monitorPage
            else:
                editorPage = childPage.get('editor')
                if editorPage:
                    page = editorPage
                else:
                    page = None
            if page:
                page['source'] = datasource['source']
                pages.append(page)
    pages.sort(key=lambda page: (page['source'].get('charts') and page.get('published'))
                or page['source']['added'], reverse=True)
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
        resultTopic = topic.get('ui')
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
    if topicHistory:
        pages = []
        for child in topicHistory['pages']:
            if child['source'].get('slug') == sourceSlug:
                if 'name' not in datasource:
                    datasource['name'] = child['source']['name']
                editorPage = child['page']['editor']
                pages.append(editorPage)
        datasource['pages'] =  pages

    foundTopic = modelapi.getDisplayTopic(topicSlug)
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
            source = datasource['source']
            if source.get('slug') in datasourceIds:
                continue
            suggestId = ''
            parts = source['slug'].split('.')
            if len(parts) > 1:
                suggestId = parts[1]
            result.append({
                'slug': source['slug'],
                'name': source['name'],
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

