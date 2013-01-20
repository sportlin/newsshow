
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

def getTopicHomeLatest():
    site = cmapi.getItemValue('site', {})
    hours = site.get('topic.home.latest', 10)
    return hours

def getHomeTopicSlug():
    return 'home'

