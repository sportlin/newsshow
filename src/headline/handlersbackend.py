import logging

from google.appengine.api import taskqueue
import webapp2

import globalconfig
import globalutil
from sourcenow import snapi
from hotword import hwapi
from hotevent import heapi

class Start(webapp2.RequestHandler):

    def get(self):
        if not self.request.get('force') and not globalutil.isBackendsTime():
            logging.info('Now is not backends time.')
            return
        taskqueue.add(queue_name='words', url='/backends/run/')


def _runTask():
    wordsConfig = globalconfig.getWordsConfig()

    pages = snapi.getSitePages()
    allWords, latestWords = hwapi.calculateTopWords(wordsConfig, 'sites', pages)
    heapi.summarizeEvents('sites', allWords[:5])
    heapi.summarizeEvents('sites', latestWords[:5])


    pages = snapi.getChartsPages()
    allWords, latestWords = hwapi.calculateTopWords(wordsConfig, 'chartses', pages)
    heapi.summarizeEvents('chartses', allWords[:5])
    heapi.summarizeEvents('chartses', latestWords[:5])


class Run(webapp2.RequestHandler):

    def post(self):
        try:
            _runTask()
        except Exception:
            logging.exception('Failed to execute _calculateWords.')

