import datetime
import json
import logging

from google.appengine.api import taskqueue

import webapp2

from commonutil import dateutil, networkutil
import globalutil
from . import models
from sourcenow import snapi
from hotevent import heapi

class WordsAddRequest(webapp2.RequestHandler):

    def post(self):
        rawdata = self.request.body
        taskqueue.add(queue_name="default", payload=rawdata, url='/words/add/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')

def _saveWords(keyname, words, pages):
    for word in words:
        keywords = []
        keywords.append(word['name'])
        if word.get('children', []):
            keywords.append(word['children'][0]['name'])
        word['keywords'] = keywords

        matched = globalutil.search(pages, keywords)
        if matched:
            wordPage = max(matched, key=lambda page: page['grade'])
            word['page'] = wordPage
    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())
    data = {
            'updated': nnow,
            'words': words,
        }
    models.saveWords(keyname, data)

class WordsAddResponse(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        data = json.loads(self.request.body)

        uuid = data.get('uuid')
        if networkutil.isUuidHandled(uuid):
            message = 'HeadlineAddResponse: %s is already handled.' % (uuid, )
            logging.warn(message)
            self.response.out.write(message)
            return
        networkutil.updateUuids(uuid)

        sitePages = snapi.getSitePages()
        chartsPages = snapi.getChartsPages()

        siteWords = data.get('sites')
        if siteWords:
            _saveWords('sites', siteWords, sitePages)
            heapi.summarizeEvents('sites', siteWords)

        chartsWords = data.get('chartses')
        if chartsWords:
            _saveWords('chartses', chartsWords, chartsPages)
            heapi.summarizeEvents('chartses', chartsWords)

        channelsWords = data.get('channels', {})
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
            topicWords = channelsWords.get(slug)
            if topicWords:
                _saveWords(slug, topicWords, topicPages)

        self.response.out.write('Done.')

