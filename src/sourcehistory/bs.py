from headline import modelapi

def getTopicHistory(slug):
    foundTopic = modelapi.getDisplayTopic(slug)
    if not foundTopic:
        return None
    topicHistory = modelapi.getTopicHistory(slug)
    resultTopic = foundTopic.get('ui')
    if topicHistory:
        pages = []
        for child in topicHistory['pages']:
            monitorPage = child['page'].get('monitor')
            editorPage = child['page'].get('editor')
            if editorPage:
                editorPage['source'] = child['source']
                if monitorPage:
                    if 'keyword' in monitorPage:
                        editorPage['keyword'] = monitorPage['keyword']
                    if 'rank' in monitorPage:
                        editorPage['rank'] = monitorPage['rank']
                pages.append(editorPage)
        resultTopic['pages'] = pages
    return resultTopic

def getTopicPicture(slug):
    foundTopic = modelapi.getDisplayTopic(slug)
    if not foundTopic:
        return None
    topicHistory = modelapi.getTopicHistory(slug)
    resultTopic = foundTopic.get('ui')
    pages = []
    if topicHistory:
        for child in topicHistory['pages']:
            monitorPage = child['page'].get('monitor')
            if monitorPage and 'img' in monitorPage:
                pages.append(monitorPage)
            else:
                editorPage = child['page'].get('editor')
                if editorPage and 'img' in editorPage:
                    pages.append(editorPage)
    resultTopic['pages'] = pages
    return resultTopic

