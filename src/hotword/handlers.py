from headline.handlers import MyHandler
from . import hwapi

class Show(MyHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        templateValues = {
            'words': hwapi.getJsonWords(),
        }
        self.render(templateValues, 'words.html')

