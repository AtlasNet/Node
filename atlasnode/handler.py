import logging

from atlasnode.protocol.Node.ttypes import *
import atlasnode


class Handler (object):
    def ping(self):
        return 1

    def getInfo(self):
        return atlasnode.info

    def hello(self, info):
        self.node_info = info
        logging.debug('Node %s joined the network through this node' % info.get_name())
        for client in atlasnode.nodes.connect_all():
            client.client.registerNode(info, atlasnode.info)
        atlasnode.nodes.register(info)

    def registerNode(self, info, via):
        if info.get_descriptor() != atlasnode.info.get_descriptor():
            logging.debug('Node %s joined the network via %s' % (info.get_name(), via.get_name()))
            atlasnode.nodes.register(info)

    def getKnownNodes(self):
        return [
            x.node_info 
            for x in atlasnode.nodes.connect_all()
            if x.node_info.get_descriptor() != self.node_info.get_descriptor()
        ] + [atlasnode.info]

    def release(self):
        pass