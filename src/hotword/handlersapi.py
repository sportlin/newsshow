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
        if not self.request.get('force') and not globalutil.isBackendsTime():
            logging.info('Now is not backends time.')
            return
        taskqueue.add(queue_name='words', url='/words/run/')

def _populateWords(stopWords, similarRate, hours, pages):
    start = dateutil.getHoursAs14(hours)
    pages = [ page for page in pages if page['added'] >= start ]
    words = bs.getTopWords(pages, stopWords)
    bs.mergeWords(similarRate, pages, words)
    for word in words:
        keywords = []
        keywords.append(word['name'])
        for childWord in word.get('children', []):
            keywords.append(childWord['name'])
        matched = snapi.search(pages, keywords)
        wordPage = max(matched, key=lambda page: page['grade'])
        word['page'] = wordPage
    return words

def _saveWords(stopWords, similarRate, keyname, allHours, latestHours, pages):
    allWords = _populateWords(stopWords, similarRate, allHours, pages)
    latestWords = _populateWords(stopWords, similarRate, latestHours, pages)
    bs.saveWords(similarRate, keyname, allHours, allWords, latestHours, latestWords)

def _calculateWords():
    wordsConfig = globalconfig.getWordsConfig()
    stopWords = wordsConfig['stop']
    similarRate = wordsConfig['similar']
    pages = snapi.getSitePages()

    allHours = wordsConfig['hours.all']
    latestHours = wordsConfig['hours.latest']
    _saveWords(stopWords, similarRate, 'sources', allHours, latestHours, pages)

class Run(webapp2.RequestHandler):

    def post(self):
        try:
            _calculateWords()
        except Exception:
            logging.exception('Failed to execute _calculateWords.')

