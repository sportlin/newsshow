import webapp2

def populateSourceUrl(pages):
    for page in pages:
        page['source']['url'] = webapp2.uri_for('datasource.history',
                                    slug=page['source']['slug'])
