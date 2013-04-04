import webapp2

def populateSourceUrl(pages):
    for page in pages:
        if 'keyword' in page:
            continue
        page['source']['url'] = webapp2.uri_for('datasource.history',
                                    source=page['source']['slug'])

