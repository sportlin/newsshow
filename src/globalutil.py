import datetime

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

