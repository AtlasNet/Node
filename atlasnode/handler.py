import logging

from atlasnode.protocol.Node.ttypes import *
import atlasnode


class Handler (object):
    def ping(self):
        return 1

    def getInfo(self):
        return atlasnode.info

    def hello(self, info):
        logging.info('Node %s joined the network through this node' % info.get_name())
        for client in atlasnode.nodes.connect_all():
            client.client.registerNode(info, atlasnode.info)
        atlasnode.nodes.register(info)

    def registerNode(self, info, via):
        logging.info('Node %s joined the network via %s' % (info.get_name(), via.get_name()))
        atlasnode.nodes.register(info)

    def release(self):
        pass