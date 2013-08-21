import json
import logging

from atlasnode.client import Client


protocol_version = 1


class Config (dict):
    def load(self, path):
        self.path = path
        self.clear()
        self.update(json.load(open(path)))

    def save(self):
        open(self.path, 'w').write(json.dumps(self, indent=True))


class Nodes (object):
    def __init__(self):
        self.clients = {}

    def load(self, lst):
        for descriptor in lst:
            self.clients[tuple(descriptor)] = None

    def list(self):
        return self.clients.keys()

    def register(self, info):
        self.clients.setdefault(info.get_descriptor(), None)
        logging.info('Registered node %s. Current network volume: %i' % (info.get_name(), len(self.clients)))

    def connection(self, descriptor, retry=True):
        descriptor = tuple(descriptor)
        if not self.clients[descriptor]:
            self.clients[descriptor] = Client(*descriptor)
            self.clients[descriptor].connected = False
        try:
            client = self.clients[descriptor]
            if not client.connected:
                client.connect()
            client.connected = True
            client.client.ping()
            return client
        except Exception, e:
            if retry:
                return self.connection(descriptor, retry=False)
            else:
                logging.info('Losing node %s:%i (%s)' % (descriptor + (e.message,)))
                self.clients.pop(descriptor)
                return None

    def connect_all(self):
        for descriptor in list(self.list()):
            client = self.connection(descriptor)
            if client:
                yield client

    def release(self):
        for client in self.clients.values():
            if client:
                client.disconnect()


config = Config()
nodes = Nodes()