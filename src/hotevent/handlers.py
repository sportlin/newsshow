import webapp2

from commonutil import stringutil

import globalutil
from headline.handlers import MyHandler
from . import models
from . import heapi


class Event(MyHandler):

    def get(self, eventScope, eventId):
        event = models.getEvent(eventScope, eventId)
        if not event:
            self.error(404)
            return
        event['pages'].sort(key=lambda page: page.get('published')
                                or page['added'], reverse=True)
        if 'keyword' in self.extraValues:
            import jieba # May fail to load jieba
            jieba.initialize(usingSmall=True)
            words = list(jieba.cut(self.extraValues['keyword'], cut_all=False))
            for page in event['pages']:
                page['grade'] = 0
                for word in words:
                    if len(word) <= 1:
                        continue
                    if stringutil.contains(page.get('title', ''), word):
                        page['grade'] += len(word)
            event['pages'].sort(key=lambda page: page['grade'], reverse=True)
        templateValues = {
            'event': event,
        }
        self.render(templateValues, 'event.html')


class Events(MyHandler):

    def get(self):
        siteEvents = heapi.getEventPages('sites')
        siteEvents = [ page for page in siteEvents if page['event']['exposed'] ]
        for page in siteEvents:
            page['event']['url'] = webapp2.uri_for('event', eventScope='sites', eventId=page['event']['id'])
        siteEvents.sort(key=lambda page: page['weight'], reverse=True)
        globalutil.populateSourceUrl(siteEvents)

        chartsEvents = heapi.getEventPages('chartses')
        chartsEvents = [ page for page in chartsEvents if page['event']['exposed'] ]
        for page in chartsEvents:
            page['event']['url'] = webapp2.uri_for('event', eventScope='chartses', eventId=page['event']['id'])
        chartsEvents.sort(key=lambda page: page['weight'], reverse=True)
        templateValues = {
            'siteEvents': siteEvents,
            'chartsEvents': chartsEvents,
        }
        self.render(templateValues, 'hot.html')

