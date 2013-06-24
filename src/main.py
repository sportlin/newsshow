import webapp2
import os
import sys
import urllib

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import templateutil.filters

import headline.handlersadmin
import headline.handlersapi
import headline.handlers
import sourcenow.handlers
import sourcehistory.handlers

import hotword.handlersapi
import hotword.handlers
import hotevent.handlers

import globalconfig


def imageproxy(imageurl, server):
    if not server:
        return imageurl
    return server + '/image/?url=' + urllib.quote(imageurl.encode('utf-8'))

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'html', 'templates'),
    'filters': {
        'utc14duration': templateutil.filters.utc14duration,
        'd14format': templateutil.filters.d14format,
        'tojson': templateutil.filters.tojson,
        'imageproxy': imageproxy,
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols', 'jinja2.ext.with_'],
    },
}

config['webapp2_extras.sessions'] = {
    'secret_key': 'dsdfsdfdsffds',
}

app = webapp2.WSGIApplication([
('/', headline.handlers.Home),
webapp2.Route('/search/<keyword:.*>', handler=headline.handlers.Search, name='search'),
('/admin/clean/', headline.handlersadmin.CleanData),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),

webapp2.Route('/latest/', handler=sourcenow.handlers.Latest, name='latest'),
webapp2.Route('/latest/<scope>/', handler=sourcenow.handlers.Latest, name='latestScope'),
webapp2.Route('/sites/', handler=sourcenow.handlers.Sites, name='sites'),
webapp2.Route('/chartses/', handler=sourcenow.handlers.Chartses, name='chartses'),
webapp2.Route('/charts/<charts:.+>', handler=sourcenow.handlers.Charts, name='charts'),
webapp2.Route('/channel/<channel>/', handler=sourcenow.handlers.Channel, name='channel'),
webapp2.Route('/source/<source:.+>', handler=sourcehistory.handlers.DatasourceHistory, name='datasource.history'),

('/words/show/', hotword.handlers.Show),
('/api/words/add/', hotword.handlersapi.WordsAddRequest),
('/words/add/', hotword.handlersapi.WordsAddResponse),

webapp2.Route('/hot/', handler=headline.handlers.Hot, name='hot'),
webapp2.Route('/event/<eventScope:[^/]+>/<eventId:[^/]+>/', handler=hotevent.handlers.Event, name='event'),
webapp2.Route('/hidden/event/<eventScope:[^/]+>/<eventId:[^/]+>/', handler=hotevent.handlers.Event, name='hidden-event'),
],
debug=os.environ['SERVER_SOFTWARE'].startswith('Dev'), config=config)

