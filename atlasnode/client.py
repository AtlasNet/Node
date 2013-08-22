from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from atlasnode.protocol.Node.ttypes import *
from atlasnode.protocol.Node import AtlasNode


class Client (object):
    def __init__(self, node):
        transport = TSocket.TSocket(str(node.host), int(node.port))
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = AtlasNode.Client(protocol)
    
    def connect(self):
        self.transport.open()
        self.node_info = self.client.getInfo()

    def disconnect(self):
        self.transport.close()
