import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import templateutil.filters

import configmanager.handlers
import headline.handlersapi
import headline.handlers

import globalconfig

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'html', 'templates'),
    'filters': {
        'utc14duration': templateutil.filters.utc14duration
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols'],
    },
}

app = webapp2.WSGIApplication([
('/', headline.handlers.Home),
('/hello/', MainPage),
('/configitem/', configmanager.handlers.MainPage),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),
('/headline/clean/request/', headline.handlersapi.HeadlineCleanRequest),
('/headline/clean/', headline.handlersapi.HeadlineCleanResponse),
('/t/', headline.handlers.Topics),
('/d/', headline.handlers.Datasources),
webapp2.Route('/topic/<slug>/', handler=headline.handlers.Topic, name='topic'),
('/latest/', headline.handlers.TopicHistory),
webapp2.Route('/latest/<slug>/', handler=headline.handlers.TopicHistory, name='latest'),
],
debug=True, config=config)

