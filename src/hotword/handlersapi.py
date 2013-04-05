
from google.appengine.api import taskqueue
import webapp2

from . import bs

class Start(webapp2.RequestHandler):

    def get(self):
        taskqueue.add(queue_name='words', url='/words/run/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Scheduler is started.')

class Run(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        words = bs.calculateTopWords()
        bs.saveWords(words)

