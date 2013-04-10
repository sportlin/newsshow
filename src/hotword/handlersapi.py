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

def _populateWords(stopWords, similarRate, hours, pages):
    start = dateutil.getHoursAs14(hours)
    pages = [ page for page in pages if page['added'] >= start ]
    words = bs.getTopWords(pages, stopWords)
    bs.mergeWords(similarRate, pages, words)
    return words

def _saveWords(stopWords, similarRate, keyname, allHours, latestHours, pages):
    allWords = _populateWords(stopWords, similarRate, allHours, pages)
    latestWords = _populateWords(stopWords, similarRate, latestHours, pages)
    bs.saveWords(similarRate, keyname, allHours, allWords, latestHours, latestWords)

class Run(webapp2.RequestHandler):

    def post(self):
        wordsConfig = globalconfig.getWordsConfig()
        stopWords = wordsConfig['stop']
        similarRate = wordsConfig['similar']
        pages = snapi.getSitePages()

        allHours = wordsConfig['hours.all']
        latestHours = wordsConfig['hours.latest']
        _saveWords(stopWords, similarRate, 'sources', allHours, latestHours, pages)

