import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import templateutil.filters

import configmanager.handlers
import headline.handlersapi
import headline.handlers

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'headline', 'templates'),
    'filters': {
        'utc14duration': templateutil.filters.utc14duration
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols'],
    },
}

app = webapp2.WSGIApplication([
('/hello/', MainPage),
('/configitem/', configmanager.handlers.MainPage),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),
('/headline/clean/request/', headline.handlersapi.HeadlineCleanRequest),
('/headline/clean/', headline.handlersapi.HeadlineCleanResponse),
('/', headline.handlers.ListPage),
('/i/', headline.handlers.IndexPage),
('/l/', headline.handlers.ListPage),
],
debug=True, config=config)

