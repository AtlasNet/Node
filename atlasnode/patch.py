import gevent
from thrift.transport import TSocket
from atlasnode.protocol.Node.ttypes import *


# Patch Thrift
TSocket.socket = gevent.socket


def ani_get_name(self):
    return '%s:%i (%s)' % (self.host, self.port, self.name)

def ani_get_descriptor(self):
    return (self.host, self.port)

AtlasNodeInfo.get_name = ani_get_name
AtlasNodeInfo.get_descriptor = ani_get_descriptor