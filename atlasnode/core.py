import logging
import gevent
import gevent.socket
import random
import signal
import sys

from gevent_thrift import TGEventServer
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol

from atlasnode.protocol.Node.ttypes import *
from atlasnode.protocol.Node import AtlasNode
from atlasnode.handler import Handler

import atlasnode
from atlasnode.nodes import Nodes
import atlasnode.log
import atlasnode.orm
import atlasnode.patch


def bootstrap():
    bootstrap_node = None
    known_nodes = atlasnode.config.get('known_nodes', [])

    atlasnode.nodes = Nodes()
    atlasnode.nodes.add_bootstrap_nodes(known_nodes)
    shuffled_nodes = atlasnode.nodes.shuffle()

    for node in shuffled_nodes:
        logging.info('Probing node %s' % node.get_name())
        client = atlasnode.nodes.connection(node)
        if client:
            client.connect()
            logging.info('Received info:' + str(client.node_info))
            logging.info('Selecting %s as the bootstrap node' % client.node_info.get_name())
            bootstrap_node = client
            break

    if not bootstrap_node:
        logging.warn('No bootstrap node available, running blind!')
    else:
        logging.info('Registering on the network')
        bootstrap_node.client.hello(atlasnode.info)
        nodes = bootstrap_node.client.getKnownNodes()
        atlasnode.nodes.replace_all(nodes)
        logging.info('Bootstrap complete with %i nodes in the list' % len(nodes))


def run():
    atlasnode.info = AtlasNodeInfo()
    atlasnode.info.host = atlasnode.config['host']
    atlasnode.info.port = atlasnode.config['port']
    atlasnode.info.name = atlasnode.config['name']
    atlasnode.info.protocolVersion = atlasnode.protocol_version
        
    logging.info('This is node %s' % atlasnode.info.get_name())

    gevent.spawn(bootstrap)

    def stop():
        #if atlasnode.nodes.list():
        #    atlasnode.config['known_nodes'] = atlasnode.nodes.list()
        atlasnode.config.save()
        sys.exit(0)

    gevent.signal(signal.SIGTERM, stop)

    # Create server
    processor = lambda: AtlasNode.Processor(Handler())
    transport = TSocket.TServerSocket(
        host=atlasnode.config['host'],
        port=atlasnode.config['port'],
    )
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    logging.info('Accepting connections on %s:%i' % (transport.host, transport.port))
    server = TGEventServer(processor, transport, tfactory, pfactory)

    try:
        server.serve()
    except KeyboardInterrupt:
        stop()
