from headline.handlers import MyHandler
from . import hwapi, bs

class Show(MyHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        words = []
        if self.request.get('test'):
            words, _ = bs.calculateTopWords()
        templateValues = {
            'words': hwapi.getJsonWords(),
            'originWords': words,
        }
        self.render(templateValues, 'words.html')

