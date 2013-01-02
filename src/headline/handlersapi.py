import logging

from google.appengine.api import taskqueue

import webapp2

import jsonpickle

from . import hlapi

class HeadlineAddRequest(webapp2.RequestHandler):
    def post(self):
        rawdata = self.request.body
        taskqueue.add(queue_name="default", payload=rawdata, url='/headline/add/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')


class HeadlineAddResponse(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        data = jsonpickle.decode(self.request.body)
        items = data['items']
        hlapi.saveItems(items)
        self.response.out.write('Done.')

