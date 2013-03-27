
import logging

from commonutil import collectionutil

from . import models

def _isPageMatched(pageTags, tags):
    matched = False
    for tag in tags:
        if collectionutil.fullContains(pageTags, tag.split('+')):
            matched = True
            break
    return matched

def _getPagesByTags(pages, tags, returnMatched=True):
    result = []
    for page in pages:
        pageTags = page['source']['tags']
        matched = _isPageMatched(pageTags, tags)
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
    pages.sort(key=lambda page: page.get('added'), reverse=True)
    return pages

def getTopicInStatus(topicSlug):
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

def _getTopicGroups(groups, slugs):
    groupConfig = {}
    for group in groups:
        groupConfig[group.get('slug')] = group
    result = []
    for groupSlug in slugs:
        group = groupConfig.get(groupSlug)
        if group:
            result.append(group)
    if not result:
        result = groups
    return result

def _populateTopicGroups(pages, foundTopic):
    groups = _getTopicGroups(models.getDisplayGroups(), foundTopic.get(
                'groups', []))
    topicGroups = _getTopicPageGroups(foundTopic, pages, groups)
    foundTopic['groups'] = topicGroups

def getTopicInGroup(topicSlug):
    foundTopic = models.getDisplayTopic(topicSlug)
    if not foundTopic:
        return None
    pages = _getAllPages()
    _populateTopicGroups(pages, foundTopic)
    return foundTopic

def _getTopicPageGroups(topic, pages, groups, maxGroups=-1):
    topicTags = topic.get('tags')
    if not topicTags:
        return None
    topicPages = _getPagesByTags(pages, topicTags)
    if not topicPages:
        return None
    topicGroups = []
    usedTags = set()
    validCount = 0
    lastValidGroup = None
    lastTags = None
    for group in groups:
        groupTags = group.get('tags')
        if not groupTags:
            continue
        groupPages = _getPagesByTags(topicPages, groupTags)
        if not groupPages:
            continue
        validCount += 1
        topicGroup = {}
        topicGroup['slug'] = group.get('slug')
        topicGroup['name'] = group.get('name')
        topicGroup['pages'] = groupPages
        if validCount == maxGroups:
            lastValidGroup = topicGroup
            lastTags = groupTags
            break
        else:
            usedTags.update(groupTags)
            topicGroups.append(topicGroup)
    if usedTags:
        allMatched = False
        if lastTags:
            maxTags = set(usedTags)
            maxTags.update(lastTags)
            unmatcheds = _getPagesByTags(topicPages, list(maxTags),
                                    returnMatched=False)
            if not unmatcheds:
                # If the last group is added, all pages are matched.
                # Then unmachedgroup is not needed.
                # And the last group take the place which was reserved for unmatched group.
                topicGroups.append(lastValidGroup)
                allMatched = True
        if not allMatched:
            unmatcheds = _getPagesByTags(topicPages, list(usedTags),
                                    returnMatched=False)
    else:# no group is available, all is seen as unmatched.
        unmatcheds = topicPages
    if unmatcheds:
        unknownGroup = {
            'slug': 'unknown',
            'name': '',
            'pages': unmatcheds,
        }
        topicGroups.append(unknownGroup)

    return topicGroups

def getTopicInPicture(slug):
    foundTopic = models.getDisplayTopic(slug)
    if not foundTopic:
        return None
    pages = _getAllPages()
    pages = [page for page in pages if 'img' in page]
    _populateTopicGroups(pages, foundTopic)
    return foundTopic

def getTopics(groupCount):
    defaultGroups = models.getDisplayGroups()
    topics = models.getDisplayTopics()
    pages = _getAllPages()
    pages = [page for page in pages if page.get('rank') == 1]
    resultTopics = []
    _GROUP_ITEMS = 6
    for topic in topics:
        groups = _getTopicGroups(defaultGroups, topic.get('groups', []))
        topicGroups = _getTopicPageGroups(topic, pages, groups, maxGroups=groupCount)
        if topicGroups:
            topic['groups'] = topicGroups
            resultTopics.append(topic)
    return resultTopics

def getChartses():
    chartses = models.getChartses()
    chartses.sort(key=lambda charts: charts['source']['added'], reverse=True)
    return chartses
