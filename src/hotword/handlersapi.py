import datetime
import json
import logging

from google.appengine.api import taskqueue

import webapp2

from commonutil import dateutil, networkutil
import globalconfig
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
    matchedWords = []
    for word in words:
        keywords = []
        keywords.append(word['name'])
        if word.get('children', []):
            keywords.append(word['children'][0]['name'])
        word['keywords'] = keywords

        matched = globalutil.search(pages, keywords)
        if matched:
            wordPage = matched[0]
            word['page'] = wordPage
            matchedWords.append(word)
    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())
    data = {
            'updated': nnow,
            'words': matchedWords,
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

        eventCriterion = globalconfig.getEventCriterion()
        sitePages = snapi.getSitePages()
        chartsPages = snapi.getChartsPages()

        siteWords = data.get('sites')
        if siteWords:
            _saveWords('sites', siteWords, sitePages)
            heapi.summarizeEvents(eventCriterion, 'sites', siteWords, sitePages)

        chartsWords = data.get('chartses')
        if chartsWords:
            _saveWords('chartses', chartsWords, chartsPages)
            heapi.summarizeEvents(eventCriterion, 'chartses', chartsWords, chartsPages)

        channelsWords = data.get('channels', {})
        channels = snapi.getChannels()
        for channel in channels:
            slug = channel.get('slug')
            if not slug:
                continue
            tags = channel.get('tags')
            if not tags:
                continue
            channelPages = snapi.getPagesByTags(sitePages, tags)
            if not channelPages:
                continue
            channelWords = channelsWords.get(slug)
            if channelWords:
                _saveWords(slug, channelWords, channelPages)

        self.response.out.write('Done.')

