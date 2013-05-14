from headline.handlers import MyHandler
from . import models

class Event(MyHandler):

    def get(self, eventScope, eventId):
        event = models.getEvent(eventScope, eventId)
        if not event:
            self.error(404)
            return
        templateValues = {
            'event': event,
        }
        self.render(templateValues, 'event.html')

