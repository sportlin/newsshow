
from commonutil import stringutil, collectionutil

from headline import modelapi

def _getPagesByTags(pages, tags):
    result = []
    for page in pages:
        pageTags = page.get('source').get('tags', [])
        if not collectionutil.fullContains(pageTags, tags):
            continue
        result.append(page)
    return result

def getTopicStatus(topicSlug):
    foundTopic = modelapi.getDisplayTopic(topicSlug)
    if not foundTopic:
        return None
    datasources = modelapi.getDatasources()
    pages = []
    for datasource in datasources:
        for childPage in datasource['pages']:
            childPage['source'] = datasource['source']
            pages.append(childPage)
    pages.sort(key=lambda page: (page['source'].get('charts') and page.get('published'))
                or page['source']['added'], reverse=True)

    resultTopic = foundTopic.get('ui')
    topicTags = foundTopic.get('tags')
    if topicTags:
        topicPages = _getPagesByTags(pages, topicTags)
        if topicPages:
            resultTopic['pages'] = topicPages
    return resultTopic

def _prepareDatasource4Show(datasourceIds, datasources):
    for datasource in datasources:
        datasourceId = datasourceIds.get(datasource['source'].get('slug'))
        if datasourceId:
            datasource['source']['id'] = datasourceId
        pages = datasource['pages']

def getTopicGroup(topicSlug):
    foundTopic = modelapi.getDisplayTopic(topicSlug)
    if not foundTopic:
        return None
    datasources = modelapi.getDatasources()
    groups = modelapi.getTopicGroups(topicSlug)
    if not groups:
        groups = modelapi.getDisplayGroups()

    resultTopic = resultTopic = foundTopic.get('ui')
    topicGroups = _getTopicGroups(foundTopic, datasources, groups)
    if topicGroups:
        # populate datasource id for datasources, as exposed id.
        datasourceIds = modelapi.getDisplayDatasourceIds(onlyActive=True)
        for topicGroup in topicGroups:
            _prepareDatasource4Show(datasourceIds, topicGroup['datasources'])
        resultTopic['groups'] = topicGroups
    return resultTopic

def _getUnmatchedDatasources(datasources, items):
    result = []
    for datasource in datasources:
        datasourceTags = datasource.get('source').get('tags', [])
        matched = False
        for item in items:
            tags = item.get('tags')
            if not tags:
                continue
            if collectionutil.fullContains(datasourceTags, tags):
                matched = True
                break
        if not matched:
            result.append(datasource)
    if result:
        result = _sortDatasources(result, orderField='added', reverse=True)
    return result

def getDatasourcesByTags(datasources, tags):
    result = []
    for datasource in datasources:
        datasourceTags = datasource.get('source').get('tags', [])
        if not tags:
            continue
        if not collectionutil.fullContains(datasourceTags, tags):
            continue
        result.append(datasource)
    return result

def _sortDatasources(datasources, orderField='order', reverse=False):
    return sorted(datasources, key=lambda source:
                source.get(orderField) if source.get(orderField)
                else stringutil.getMaxOrder(), reverse=reverse)

def _getTopicGroups(topic, datasources, groups):
    topicTags = topic.get('tags')
    if not topicTags:
        return None
    topicDatasources = getDatasourcesByTags(datasources, topicTags)
    if not topicDatasources:
        return None
    topicGroups = []
    for group in groups:
        groupTags = group.get('tags')
        if not groupTags:
            continue
        groupDatasources = getDatasourcesByTags(topicDatasources, groupTags)
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

