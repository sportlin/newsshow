
from configmanager import cmapi

def getSiteConfig():
    return cmapi.getItemValue('site',
        {'name': 'Site Name'})

def getI18N():
    return cmapi.getItemValue('i18n',
        {'home': 'Home'})

def getChannels():
    return cmapi.getItemValue('channels', [])

def getChannel(slug):
    channels = getChannels()
    for channel in channels:
        if channel.get('slug') == slug:
            return channel
    return None

def getHomeTags():
    return cmapi.getItemValue('home.tags', [])

def getHomeTag(slug):
    homeTags = getHomeTags()
    for homeTag in homeTags:
        if homeTag.get('slug') == slug:
            return homeTag
    return None

def getSiteLatestHours():
    site = cmapi.getItemValue('site', {})
    hours = site.get('latest.hours', 24)
    return hours

def getDatasourceDays():
    site = cmapi.getItemValue('site', {})
    days = site.get('datasource.days', 7)
    return days

def getEventCriterion():
    result = cmapi.getItemValue('event.criterion', {})
    if 'expose.pages' not in result:
        result['expose.pages'] = 5
    return result

def getTwitterAccount():
    return cmapi.getItemValue('twitter.account', {})

