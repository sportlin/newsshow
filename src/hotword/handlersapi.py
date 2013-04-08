import logging

from google.appengine.api import taskqueue
import webapp2

from . import bs

class Start(webapp2.RequestHandler):

    def get(self):
        if not bs.isBackendsTime():
            logging.info('Now is not backends time.')
            return
        taskqueue.add(queue_name='words', url='/words/run/')

class Run(webapp2.RequestHandler):

    def post(self):
        _, words = bs.calculateTopWords()
        bs.saveWords(words)

