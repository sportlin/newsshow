
import os

from configmanager import cmapi

def getSiteConfig():
    return cmapi.getItemValue('site',
        {'name': 'Site Name'})

def getI18N():
    return cmapi.getItemValue('i18n',
        {'home': 'Home'})

def getSiteLatestHours():
    site = cmapi.getItemValue('site', {})
    hours = site.get('latest.hours', 24)
    return hours

def getTopicHistoryHours():
    site = cmapi.getItemValue('site', {})
    hours = site.get('topic.hours', 24)
    return hours

def getDatasourceDays():
    site = cmapi.getItemValue('site', {})
    days = site.get('datasource.days', 7)
    return days

def getTopicHomeLatest():
    site = cmapi.getItemValue('site', {})
    hours = site.get('topic.home.latest', 10)
    return hours

def getBackendsConfig():
    return cmapi.getItemValue('backends', {})

def getWordsConfig():
    result = cmapi.getItemValue('words', {})
    if 'stop' not in result:
        result['stop'] = []
    if 'similar' not in result:
        result['similar'] = {
                '0': 6
            }
    if 'hours.all' not in result:
        result['hours.all'] = 24
    if 'hours.latest' not in result:
        result['hours.latest'] = 4
    return result

def getStopWords():
    return cmapi.getItemValue('words.stop', [])

