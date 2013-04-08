import datetime

import webapp2

from pytz.gae import pytz

import globalconfig

def populateSourceUrl(pages):
    for page in pages:
        if 'keyword' in page:
            continue
        page['source']['url'] = webapp2.uri_for('datasource.history',
                                    source=page['source']['slug'])
def isBackendsTime():
    site = globalconfig.getSiteConfig()
    timezonename = site.get('timezone')
    if not timezonename:
        return True
    backendsConfig = site.get('backends')
    if not backendsConfig:
        return True
    hours = backendsConfig.get('hours')
    if not hours:
        return True
    nnow = datetime.datetime.now(tz=pytz.utc)
    tzdate = nnow.astimezone(pytz.timezone(timezonename))
    return tzdate.hour in hours

