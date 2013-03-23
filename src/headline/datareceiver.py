import logging

_DATA_RECEIVERS = []

class BasicDataReceiver(object):

    def __init__(self, name):
        self.name = name

    def onData(self, datasource, items):
        pass

def registerReceiver(receiver):
    _DATA_RECEIVERS.append(receiver)

def receive(datasource, items):
    logging.info('datareceiver.receive: %s.' % (datasource, ))
    for receiver in _DATA_RECEIVERS:
        logging.info('%s on data.' % (receiver.name, ))
        receiver.onData(datasource, items)

