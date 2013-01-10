
import os

from configmanager import cmapi

def getSiteLatestHours():
    site = cmapi.getItemValue('site', {})
    hours = site.get('latest.hours', 24)
    return hours

