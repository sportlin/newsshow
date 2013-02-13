import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import templateutil.filters

import configmanager.handlers
import headline.handlersadmin
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
        'utc14duration': templateutil.filters.utc14duration,
        'd14format': templateutil.filters.d14format,
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols', 'jinja2.ext.with_'],
    },
}

app = webapp2.WSGIApplication([
('/', headline.handlers.Home),
('/hello/', MainPage),
('/configitem/', configmanager.handlers.MainPage),
('/admin/datasource/expose/', headline.handlersadmin.DatasourceExpose),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),
('/t/', headline.handlers.Topics),
('/d/', headline.handlers.Datasources),
webapp2.Route('/topic/<slug>/', handler=headline.handlers.Topic, name='topic'),
webapp2.Route('/latest/<slug>/', handler=headline.handlers.TopicLatest, name='latest'),
webapp2.Route('/picture/<slug>/', handler=headline.handlers.TopicPicture, name='picture'),
webapp2.Route('/source/<sourceId>/', handler=headline.handlers.DatasourceHistory, name='datasource'),
],
debug=True, config=config)

