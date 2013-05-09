from commonutil import stringutil
from . import bs, models

def getDisplayTopics():
    return models.getDisplayTopics()

def getAllPages():
    sitePages = models.getPages(keyname='sites')
    chartsPages = models.getPages(keyname='chartses')
    return sitePages + chartsPages

def getSitePages():
    return models.getPages(keyname='sites')

def getChartsPages():
    return models.getPages(keyname='chartses')

def getPagesByTags(pages, tags):
    return bs.getPagesByTags(pages, tags)

