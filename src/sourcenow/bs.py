
import logging

from commonutil import collectionutil
import globalutil
from . import models

def _isPageMatched(pageTags, tags):
    matched = False
    for tag in tags:
        if collectionutil.fullContains(pageTags, tag.split('+')):
            matched = True
            break
    return matched

def getPagesByTags(pages, tags, returnMatched=True):
    result = []
    for page in pages:
        pageTags = page['source']['tags']
        matched = _isPageMatched(pageTags, tags)
        if (returnMatched and matched) or (not returnMatched and not matched):
            result.append(page)
    return result

def getChannel(slug):
    foundTopic = models.getDisplayTopic(slug)
    if not foundTopic:
        return None

    pages = sitePages = models.getPages(keyname='sites')

    topicTags = foundTopic.get('tags')
    topicPages = getPagesByTags(pages, topicTags)
    foundTopic['pages'] = topicPages

    return foundTopic

def getCharts(slug):
    chartses = models.getDatasources('chartses')
    for charts in chartses:
        if charts['source']['slug'] == slug:
            return charts
    return None

def getChartses():
    return models.getDatasources('chartses')

