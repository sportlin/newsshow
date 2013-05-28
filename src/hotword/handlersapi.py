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
        data = json.loads(self.request.body)
        uuid = data.get('uuid')
        if networkutil.isUuidHandled(uuid):
            message = 'HeadlineAddResponse: %s is already handled.' % (uuid, )
            logging.warn(message)
            self.response.out.write(message)
            return
        networkutil.updateUuids(uuid)

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
        eventCriterion = globalconfig.getEventCriterion()

        key = data['key']
        if key == 'sites':
            sitePages = snapi.getSitePages()
            _saveWords('sites', data['words'], sitePages)
            heapi.summarizeEvents(eventCriterion, 'sites', data['words'], sitePages)
        elif key == 'chartses':
            chartsPages = snapi.getChartsPages()
            _saveWords('chartses', data['words'], chartsPages)
            heapi.summarizeEvents(eventCriterion, 'chartses', data['words'], chartsPages)
        else:
            channel = snapi.getChannel(key)
            if not channel:
                logging.warn('Channel %s does not exist.' % (channel, ))
            elif not channel.get('tags'):
                logging.warn('Channel %s has no tags.' % (channel, ))
            else:
                sitePages = snapi.getSitePages()
                channelPages = snapi.getPagesByTags(sitePages, channel.get('tags'))
                if channelPages:
                    _saveWords(key, data['words'], channelPages)

        self.response.out.write('Done.')

