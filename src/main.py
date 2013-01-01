import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import configmanager.handlers
import headline.handlersapi
import headline.handlers

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')


app = webapp2.WSGIApplication([
('/hello/', MainPage),
('/configitem/', configmanager.handlers.MainPage),
('/api/headline/', headline.handlersapi.HeadlineRequest),
('/headline/save/', headline.handlersapi.HeadlineResponse),
('/', headline.handlers.HomePage),
],
                              debug=True)

