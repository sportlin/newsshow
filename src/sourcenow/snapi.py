from commonutil import stringutil
from . import bs, models

def getAllPages():
    sitePages = models.getPages(keyname='sites')
    chartsPages = models.getPages(keyname='chartses')
    return sitePages + chartsPages

def getSitePages():
    return models.getPages(keyname='sites')

def getChartsPages():
    pages = models.getPages(keyname='chartses')
    urls = set()
    result = []
    for page in pages:
        if page.get('url') in urls:
            continue
        urls.add(page.get('url'))
        result.append(page)
    return result

def getPagesByTags(pages, tags):
    return bs.getPagesByTags(pages, tags)

def getChartses():
    return bs.getChartses()

