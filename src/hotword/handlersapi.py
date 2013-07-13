import datetime
import json
import logging
import math

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

def _getNaturalKeywords(keywords, pages):
    scoreCache = {}
    for keyword in keywords:
        scoreCache[keyword] = 0

    for page in pages:
        title = page.get('title')
        if not title:
            continue
        matchedCount = 0
        matched = []
        for keyword in keywords:
            index = title.find(keyword)
            matched.append(index)
            if index >= 0:
                matchedCount += 1
        # the keyword near the start of title has more weight.
        smatched = sorted(matched, reverse=True)
        for i in range(len(matched)):
            matched[i] = smatched.index(matched[i])

        for i in range(len(keywords)):
            scoreCache[keywords[i]] += matched[i] * math.pow(10, matchedCount)
    return sorted(keywords, key=lambda keyword: scoreCache[keyword], reverse=True)

def _saveWords(keyname, words, pages):
    matchedWords = []
    for keywords in words:
        word = {}
        word['keywords'] = keywords

        matched = globalutil.search(pages, keywords)
        if matched:
            wordPage = matched[0]
            word['page'] = wordPage
            word['size'] = len(matched)
            word['readablekeywords'] = _getNaturalKeywords(keywords, matched)
            matchedWords.append(word)
    nnow = dateutil.getDateAs14(datetime.datetime.utcnow())
    data = {
            'updated': nnow,
            'words': matchedWords,
        }
    models.saveWords(keyname, data)
    return matchedWords

class WordsAddResponse(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        data = json.loads(self.request.body)
        eventCriterion = globalconfig.getEventCriterion()
        twitterAccount = globalconfig.getTwitterAccount()

        key = data['key']
        if key == 'sites':
            sitePages = snapi.getSitePages()
            matchedWords = _saveWords('sites', data['words'], sitePages)
        elif key == 'chartses':
            chartsPages = snapi.getChartsPages()
            matchedWords = _saveWords('chartses', data['words'], chartsPages)
        else:
            channel = globalconfig.getChannel(key)
            if not channel:
                logging.warn('Channel %s does not exist.' % (channel, ))
            elif not channel.get('tags'):
                logging.warn('Channel %s has no tags.' % (channel, ))
            else:
                sitePages = snapi.getSitePages()
                channelPages = snapi.getPagesByTags(sitePages, channel.get('tags'))
                if channelPages:
                    matchedWords = _saveWords(key, data['words'], channelPages)
                    heapi.summarizeEvents(eventCriterion, key, matchedWords, channelPages, twitterAccount)

        self.response.out.write('Done.')

