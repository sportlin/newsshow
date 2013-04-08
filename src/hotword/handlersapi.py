import logging

from google.appengine.api import taskqueue
import webapp2

from commonutil import dateutil

import globalconfig
import globalutil
from sourcenow import snapi
from . import bs

class Start(webapp2.RequestHandler):

    def get(self):
        if not globalutil.isBackendsTime():
            logging.info('Now is not backends time.')
            return
        taskqueue.add(queue_name='words', url='/words/run/')

def _populateWords(similarRate, hours, pages):
    start = dateutil.getHoursAs14(hours)
    pages = [ page for page in pages if page['added'] >= start ]
    words = bs.getTopWords(pages)
    bs.mergeWords(similarRate, pages, words)
    return words

def _saveWords(similarRate, keyname, allHours, latestHours, pages):
    allWords = _populateWords(similarRate, allHours, pages)
    latestWords = _populateWords(similarRate, latestHours, pages)
    bs.saveWords(similarRate, keyname, allHours, allWords, latestHours, latestWords)

class Run(webapp2.RequestHandler):

    def post(self):
        wordsConfig = globalconfig.getWordsConfig()
        similarRate = wordsConfig['similar']
        pages = snapi.getSitePages()

        allHours = wordsConfig['hours.all']
        latestHours = wordsConfig['hours.latest']
        _saveWords(similarRate, 'sources', allHours, latestHours, pages)

