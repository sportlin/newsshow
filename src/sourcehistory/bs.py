from headline import modelapi
from . import models

def getDatasourceHistory(slug):
    return models.getDatasourceHistory(slug)

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

