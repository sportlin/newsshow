from commonutil import stringutil
from . import bs, models

def getDisplayTopics():
    return models.getDisplayTopics()

def getData4Home():
    chartses = models.getDatasources('chartses')
    chartsPages = models.getPages(datasources=chartses)
    sitePages = models.getPages(keyname='datasources')
    return {
        'chartses': chartses,
        'pages': {
            'charts': chartsPages,
            'site': sitePages,
        }
    }

def search(keyword):
    sitePages = models.getPages(keyname='datasources')
    chartsPages = models.getPages(keyname='chartses')
    result = []
    for page in sitePages + chartsPages:
        if stringutil.contains(page.get('keyword', ''), keyword):
            result.append(page)
        elif stringutil.contains(page.get('title', ''), keyword):
            result.append(page)
    return result

def getSitePages():
    return models.getPages(keyname='datasources')

