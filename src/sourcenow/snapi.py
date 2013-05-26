from commonutil import stringutil
from . import bs, models

def getChannels():
    return models.getChannels()

def getChannel(slug):
    channels = getChannels()
    for channel in channels:
        if channel.get('slug') == slug:
            return channel
    return None

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

