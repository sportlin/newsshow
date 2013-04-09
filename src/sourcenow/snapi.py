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

def getAllPages():
    sitePages = models.getPages(keyname='datasources')
    chartsPages = models.getPages(keyname='chartses')
    return sitePages + chartsPages

def search(pages, keywords):
    result = []
    ksize = len(keywords)
    for page in pages:
        grade = 0
        for index, keyword in enumerate(keywords):
            # the top keyword is more important than the bottom one.
            indexBonus = (ksize - index) * 0.1
            if stringutil.contains(page.get('keyword', ''), keyword):
                grade += len(keyword) + indexBonus
            elif stringutil.contains(page.get('title', ''), keyword):
                grade += len(keyword) + indexBonus
        if grade > 0:
            page['grade'] = grade
            result.append(page)
    return result

def getSitePages():
    return models.getPages(keyname='datasources')

