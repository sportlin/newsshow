
import os

from configmanager import cmapi

def getSiteConfig():
    return cmapi.getItemValue('site',
        {
            'site': {'name': 'Site Name'},
        }
    )

def getSiteLatestHours():
    site = cmapi.getItemValue('site', {})
    hours = site.get('latest.hours', 24)
    return hours

def getTopicHistoryHours():
    site = cmapi.getItemValue('site', {})
    hours = site.get('topic.hours', 24)
    return hours

def getDatasourceHistoryDays():
    site = cmapi.getItemValue('archive', {})
    days = site.get('datasource.history.days', 7)
    return days

def getDatasourceDays():
    site = cmapi.getItemValue('archive', {})
    days = site.get('datasource.days', 30)
    return days

