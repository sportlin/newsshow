
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
        if keyword in page.get('title', ''):
            result.append(page)
    return result

