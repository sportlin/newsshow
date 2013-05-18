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
    _INTERVAL_MINUTES = 5
    backendsConfig = globalconfig.getBackendsConfig()
    if not backendsConfig:
        return True

    timezonename = backendsConfig.get('timezone')
    if not timezonename:
        return True

    freeHours = backendsConfig.get('hours.free', [])
    limitHours = backendsConfig.get('hours.limit', [])

    if not freeHours and not limitHours:
        return True

    nnow = datetime.datetime.now(tz=pytz.utc)
    tzdate = nnow.astimezone(pytz.timezone(timezonename))

    if tzdate.hour in freeHours:
        return True

    if tzdate.hour in limitHours and tzdate.minute < _INTERVAL_MINUTES:
        return True

    return False

def search(pages, keywords):
    result = []
    ksize = len(keywords)
    urls = set()
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
            if page.get('url') in urls:
                continue
            urls.add(page.get('url'))
            page['grade'] = grade
            result.append(page)
    result.sort(key=lambda page: page.get('added'), reverse=True)
    result.sort(key=lambda page: page['grade'], reverse=True)
    for page in result:
        del page['grade']
    return result

def getTodayStartAsUtc14(timezonename):
    tzdate = datetime.datetime.now(tz=pytz.utc)
    if timezonename:
        tz  = pytz.timezone(timezonename)
        tzdate = tzdate.astimezone(tz)
        tzdate = datetime.datetime(tzdate.year, tzdate.month, tzdate.day, 0, 0, 0, 0, tzinfo=tz)
        tzdate = tzdate.astimezone(pytz.utc)
    return datetime.datetime.strftime(tzdate, '%Y%m%d%H%M%S')

