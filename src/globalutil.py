import datetime
import logging

import webapp2

from pytz.gae import pytz

from commonutil import stringutil
import globalconfig

def populateSourceUrl(pages):
    for page in pages:
        if 'keyword' in page:
            continue
        page['source']['url'] = webapp2.uri_for('datasource.history',
                                    source=page['source']['slug'])

def compressContent(sentenceSeparators, pages):
    for page in pages:
        if not page.get('content'):
            continue
        page['content'] = stringutil.getFirstSentence(sentenceSeparators, page['content'])

def isBackendsTime():
    backendsConfig = globalconfig.getBackendsConfig()
    if not backendsConfig:
        return True
    hours = backendsConfig.get('hours')
    if not hours:
        return True
    timezonename = backendsConfig.get('timezone')
    if not timezonename:
        return True
    nnow = datetime.datetime.now(tz=pytz.utc)
    tzdate = nnow.astimezone(pytz.timezone(timezonename))
    return tzdate.hour in hours

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

def getTodayStartAsUtc14(timezonename):
    tzdate = datetime.datetime.now(tz=pytz.utc)
    if timezonename:
        tz  = pytz.timezone(timezonename)
        tzdate = tzdate.astimezone(tz)
        tzdate = datetime.datetime(tzdate.year, tzdate.month, tzdate.day, 0, 0, 0, 0, tzinfo=tz)
        tzdate = tzdate.astimezone(pytz.utc)
    return datetime.datetime.strftime(tzdate, '%Y%m%d%H%M%S')

