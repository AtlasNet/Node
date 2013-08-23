import gevent
from gevent.lock import RLock
import logging

from atlasnode.client import Client
from atlasnode.orm.models import Node


class Nodes (object):
    def __init__(self):
        self.clients = {}
        self.lock = RLock()

    def add_bootstrap_nodes(self, lst):
        with self.lock:
            for node in lst:
                if not Node.find(descriptor=node):
                    Node(
                        host=node[0],
                        port=node[1],
                    ).save()

    def replace_all(self, infos):
        with self.lock:
            self.disconnect_all()
            Node.objects.all().delete()
            for info in infos:
                self.register(info=info)

    def list(self):
        return Node.objects.all()

    def shuffle(self):
        return Node.objects.order_by('?').all()

    def register(self, info=None):
        if not Node.find(info=info):
            Node(
                host=info.host,
                port=info.port,
            ).save()

        logging.debug('Registered node %s. Current network volume: %i' % (info.get_name(), Node.objects.count()))

    def connection(self, node, retry=True):
        self.clients.setdefault(node.id, None)
        if not self.clients[node.id]:
            self.clients[node.id] = Client(node)
            self.clients[node.id].connected = False
        try:
            with gevent.Timeout(2):
                client = self.clients[node.id]
                with client.lock:
                    if not client.connected:
                        client.connect()
                    client.connected = True
                    client.client.ping()
                return client
        except BaseException, e:
            import traceback; traceback.print_exc();
            if retry:
                return self.connection(node, retry=False)
            else:
                logging.debug('Losing node %s (%s)' % (node.get_name(), str(e)))
                if node.id in self.clients:
                    self.clients.pop(node.id)
                return None

    def connect_all(self):
        for node in self.list():
            client = self.connection(node)
            if client:
                yield client

    def each(self, fx, timeout=2):
        def gl(node):
            with gevent.Timeout(timeout, False):
                client = self.connection(node)
                if client:
                    with client.lock:
                        return fx(client)
        return [gevent.spawn(gl, node) for node in self.list()]

    def disconnect_all(self):
        for client in self.clients.values():
            if client:
                client.disconnect()
        
    def release(self):
        self.disconnect_all()
