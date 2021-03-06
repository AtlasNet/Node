# Copyright 2012 Edgeware AB.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Server for gevent based sockets.
Based on gist by imlucas: https://gist.github.com/361144
"""

import gevent
from gevent.server import StreamServer
import traceback
import socket

from thrift.server.TServer import TServer
from thrift.transport.TTransport import TTransportException, TFileObjectTransport
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class TGEventServer(TServer):
    """Gevent socket server."""

    def serve(self):
        self.serverTransport.listen()
        while True:
            client = self.serverTransport.accept()
            gevent.spawn(self._process_socket, client)

    def _process_socket(self, client):
        """A greenlet for handling a single client."""
        itrans = self.inputTransportFactory.getTransport(client)
        otrans = self.outputTransportFactory.getTransport(client)
        iprot = self.inputProtocolFactory.getProtocol(itrans)
        oprot = self.outputProtocolFactory.getProtocol(otrans)
        processor = self.processor()
        try:
            while True:
                processor.process(iprot, oprot)
        except TTransportException:
            pass
        except socket.error:
            pass
        except Exception:
            traceback.print_exc()

        itrans.close()
        otrans.close()


class ThriftServer(StreamServer):
    """Thrift server based on StreamServer."""

    def __init__(self, log, listener, processor, inputTransportFactory=None,
                 outputTransportFactory=None, inputProtocolFactory=None,
                 outputProtocolFactory=None, **kwargs):
        StreamServer.__init__(self, listener, self._process_socket, **kwargs)
        self.log = log
        self.processor = processor
        self.inputTransportFactory = (inputTransportFactory
            or TTransport.TTransportFactoryBase())
        self.outputTransportFactory = (outputTransportFactory
            or TTransport.TTransportFactoryBase())
        self.inputProtocolFactory = (inputProtocolFactory
            or TBinaryProtocol.TBinaryProtocolFactory())
        self.outputProtocolFactory = (outputProtocolFactory
            or TBinaryProtocol.TBinaryProtocolFactory())

    def _process_socket(self, client, address):
        """A greenlet for handling a single client."""
        client = TFileObjectTransport(client.makefile())
        itrans = self.inputTransportFactory.getTransport(client)
        otrans = self.outputTransportFactory.getTransport(client)
        iprot = self.inputProtocolFactory.getProtocol(itrans)
        oprot = self.outputProtocolFactory.getProtocol(otrans)
        try:
            while True:
                self.processor.process(iprot, oprot)
        except EOFError:
            pass
        except Exception:
            self.log.exception("caught exception while processing thrift request")

        itrans.close()
        otrans.close()