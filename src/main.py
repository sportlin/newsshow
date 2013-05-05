import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import templateutil.filters

import configmanager.handlers
import headline.handlersadmin
import headline.handlersapi
import headline.handlers
import sourcenow.handlers
import sourcehistory.handlers

import hotword.handlersapi
import hotword.handlers
import hotevent.handlers

import globalconfig

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'html', 'templates'),
    'filters': {
        'utc14duration': templateutil.filters.utc14duration,
        'd14format': templateutil.filters.d14format,
        'tojson': templateutil.filters.tojson,
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols', 'jinja2.ext.with_'],
    },
}

app = webapp2.WSGIApplication([
('/', headline.handlers.Home),
webapp2.Route('/search/<keyword:.*>', handler=headline.handlers.Search, name='search'),
('/configitem/', configmanager.handlers.MainPage),
('/admin/clean/', headline.handlersadmin.CleanData),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),

webapp2.Route('/hot/', handler=sourcenow.handlers.Hot, name='hot'),
webapp2.Route('/latest/', handler=sourcenow.handlers.Latest, name='latest'),
webapp2.Route('/charts/<charts:.+>', handler=sourcenow.handlers.Charts, name='charts'),
webapp2.Route('/channel/<channel>/', handler=sourcenow.handlers.Channel, name='channel'),
webapp2.Route('/source/<source:.+>', handler=sourcehistory.handlers.DatasourceHistory, name='datasource.history'),

('/words/show/', hotword.handlers.Show),
('/api/words/add/', hotword.handlersapi.WordsAddRequest),
('/words/add/', hotword.handlersapi.WordsAddResponse),
webapp2.Route('/event/<eventScope:[^/]+>/<eventId:[^/]+>/', handler=hotevent.handlers.Event, name='event'),
],
debug=True, config=config)

