
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

