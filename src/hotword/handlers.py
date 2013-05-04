from commonutil import dateutil

import globalconfig
from headline.handlers import MyHandler
from . import hwapi

class Show(MyHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        sentenceSeparators = self.site.get('sentence.separator', [])
        words = []
        templateValues = {
            'words': hwapi.getJsonWords(sentenceSeparators),
            'originWords': words,
        }
        self.render(templateValues, 'words.html')

