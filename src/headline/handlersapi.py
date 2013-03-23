import logging

from google.appengine.api import taskqueue

import webapp2

import jsonpickle

from commonutil import networkutil

from . import datareceiver

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

        uuid = data.get('uuid')
        if networkutil.isUuidHandled(uuid):
            message = 'HeadlineAddResponse: %s is already handled.' % (uuid, )
            logging.warn(message)
            self.response.out.write(message)
            return
        networkutil.updateUuids(uuid)

        datasource = data['datasource']
        items = data['items']
        datareceiver.receive(datasource, items)
        self.response.out.write('Done.')


