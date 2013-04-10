from commonutil import dateutil

import globalconfig
from headline.handlers import MyHandler
from sourcenow import snapi
from . import hwapi, bs

class Show(MyHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        words = []
        if self.request.get('test'):
            wordsConfig = globalconfig.getWordsConfig()
            start = dateutil.getHoursAs14(wordsConfig['hours.all'])
            pages = snapi.getSitePages()
            pages = [ page for page in pages if page['added'] >= start ]
            words = bs.getTopWords(pages, [])
        templateValues = {
            'words': hwapi.getJsonWords(),
            'originWords': words,
        }
        self.render(templateValues, 'words.html')

