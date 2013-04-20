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
    stopWords = globalconfig.getStopWords()

    sitePages = snapi.getSitePages()
    allWords, latestWords = hwapi.calculateTopWords(wordsConfig, stopWords, 'sites', sitePages)
    heapi.summarizeEvents('sites', allWords, latestWords)

    pages = snapi.getChartsPages()
    allWords, latestWords = hwapi.calculateTopWords(wordsConfig, stopWords, 'chartses', pages)
    heapi.summarizeEvents('chartses', allWords, latestWords)

    topics = snapi.getDisplayTopics()
    for topic in topics:
        slug = topic.get('slug')
        if not slug:
            continue
        tags = topic.get('tags')
        if not tags:
            continue
        topicPages = snapi.getPagesByTags(sitePages, tags)
        if not topicPages:
            continue
        allWords, latestWords = hwapi.calculateTopWords(wordsConfig, stopWords, slug, topicPages)


class Run(webapp2.RequestHandler):

    def post(self):
        try:
            _runTask()
        except Exception:
            logging.exception('Failed to execute _calculateWords.')

