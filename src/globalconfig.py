
import os

from configmanager import cmapi

def getSiteLatestHours():
    site = cmapi.getItemValue('site', {})
    hours = site.get('latest.hours', 24)
    return hours

def getDatasourceHistoryDays():
    site = cmapi.getItemValue('site', {})
    days = site.get('datasource.history.days', 7)
    return days

def getDatasourceDays():
    site = cmapi.getItemValue('site', {})
    days = site.get('datasource.days', 30)
    return days

