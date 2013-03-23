
import logging

from commonutil import stringutil, collectionutil

from headline import modelapi
from . import models

def _getPagesByTags(pages, tags, returnMatched=True):
    result = []
    for page in pages:
        pageTags = page['source']['tags']
        matched = collectionutil.fullContains(pageTags, tags)
        if (returnMatched and matched) or (not returnMatched and not matched):
            result.append(page)
    return result

def _getAllPages():
    datasources = models.getDatasources()
    pages = []
    for datasource in datasources:
        for childPage in datasource['pages']:
            childPage['source'] = datasource['source']
            pages.append(childPage)
    pages.sort(key=lambda page: page['source']['added'], reverse=True)
    return pages

def getTopicStatus(topicSlug):
    foundTopic = models.getDisplayTopic(topicSlug)
    if not foundTopic:
        return None
    pages = _getAllPages()
    topicTags = foundTopic.get('tags')
    if topicTags:
        topicPages = _getPagesByTags(pages, topicTags)
        if topicPages:
            foundTopic['pages'] = topicPages
    return foundTopic

def getTopicGroup(topicSlug):
    foundTopic = models.getDisplayTopic(topicSlug)
    if not foundTopic:
        return None
    pages = _getAllPages()
    groups = models.getTopicGroups(topicSlug)
    if not groups:
        groups = models.getDisplayGroups()
    topicGroups = _getTopicGroups(foundTopic, pages, groups)
    foundTopic['groups'] = topicGroups
    return foundTopic

def _getTopicGroups(topic, pages, groups, maxGroups=-1):
    topicTags = topic.get('tags')
    if not topicTags:
        return None
    topicPages = _getPagesByTags(pages, topicTags)
    if not topicPages:
        return None
    topicGroups = []
    usedTags = set()
    if maxGroups > 0:
        groups = groups[:maxGroups - 1]
    for group in groups:
        groupTags = group.get('tags')
        if not groupTags:
            continue
        groupPages = _getPagesByTags(topicPages, groupTags)
        if not groupPages:
            continue
        usedTags.update(groupTags)
        topicGroup = {}
        topicGroup['slug'] = group.get('slug')
        topicGroup['name'] = group.get('name')
        topicGroup['pages'] = groupPages
        topicGroups.append(topicGroup)
    if usedTags:
        unmatched = _getPagesByTags(topicPages, list(usedTags),
                                    returnMatched=False)
    else:
        unmatched = pages
    if unmatched:
        unknownGroup = {
            'slug': 'unknown',
            'name': '',
            'pages': topicPages,
        }
        topicGroups.append(unknownGroup)

    return topicGroups

def getTopics4Home():
    defaultGroups = models.getDisplayGroups()
    topics = models.getDisplayTopics()
    pages = _getAllPages()
    pages = [page for page in pages if page.get('rank') == 1]
    resultTopics = []
    _MAX_GROUPS = 4
    _GROUP_ITEMS = 6
    for topic in topics:
        groups = models.getTopicGroups(topic['slug'])
        if not groups:
            groups = defaultGroups
        topicGroups = _getTopicGroups(topic, pages, groups, maxGroups=_MAX_GROUPS)
        if topicGroups:
            for topicGroup in topicGroups:
                topicGroup['pages'] = topicGroup['pages'][:_GROUP_ITEMS]
            topic['groups'] = topicGroups
            resultTopics.append(topic)
    return resultTopics

def getTopicPicture(slug):
    foundTopic = models.getDisplayTopic(slug)
    if not foundTopic:
        return None
    pages = _getAllPages()
    pages = [page for page in pages if 'img' in page]
    topicTags = foundTopic.get('tags')
    if topicTags:
        topicPages = _getPagesByTags(pages, topicTags)
        if topicPages:
            foundTopic['pages'] = topicPages
    return foundTopic

