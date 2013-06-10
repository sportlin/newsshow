import webapp2

from commonutil import stringutil

from headline.handlers import MyHandler
from . import models

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

