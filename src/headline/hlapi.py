import copy
import datetime
import logging

from commonutil import stringutil
from commonutil import dateutil, collectionutil
import globalconfig
from . import modelapi
import sourcenow.bs as bsNow

def saveItems(datasource, items):
    modelapi.updateDatasources(datasource, items)

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

def getTopicsConfig():
    return [topic.get('ui') for topic in modelapi.getDisplayTopics()]

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
            if 'added' not in childPage:
                continue
            childPage['source'] = datasource['source']
            pages.append(childPage)
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
        topicDatasources = bsNow.getDatasourcesByTags(datasources, topicTags)
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

