import logging

from headline.handlers import MyHandler
from . import models

class Event(MyHandler):

    def get(self, eventId):
        # Only expose events from sites
        scope = 'sites'
        logging.info('%s:%s' % (scope, eventId))
        event = models.getEvent(scope, eventId)
        if not event:
            self.error(404)
            return
        pages = [ word['page'] for word in event['words'] ]
        templateValues = {
            'event': event,
            'pages': pages,
        }
        self.render(templateValues, 'event.html')

