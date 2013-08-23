import logging
import os
from passlib.hash import md5_crypt

from atlasnode.protocol.Node.ttypes import *
from atlasnode.orm.models import Message, MessageListing
import atlasnode
from atlasnode import crypto


class Handler (object):
    def __init__(self):
        self.auth_challenge = os.urandom(16)
        self.auth_public_key = None
        self.auth_complete = False

    def ping(self):
        return 1

    def getInfo(self):
        return atlasnode.info

    def hello(self, info):
        self.node_info = info

    def join(self):
        logging.debug('Node %s joined the network through this node' % self.node_info.get_name())
        for client in atlasnode.nodes.connect_all():
            if client.node_info.get_descriptor() != self.node_info.get_descriptor():
                client.client.registerNode(self.node_info, atlasnode.info)
        atlasnode.nodes.register(self.node_info)

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

    def postMessage(self, message):
        msg = Message(
            data=message.data,
            recipient_key=message.recipientKey
        )
        msg.save()
        logging.debug('Received message %u', msg.id)

        listing = MessageListing(
            node_host=atlasnode.info.host,
            node_port=atlasnode.info.port,
            message_id=msg.id,
            recipient_key=msg.recipient_key,
        )
        listing.save()
        
        for client in atlasnode.nodes.connect_all():
            client.client.registerMessageListing(msg.recipient_key, msg.id)
        
    def registerMessageListing(self, recipient_key, id):
        # TODO: verify node IP
        listing = MessageListing(
            node_host=self.node_info.host,
            node_port=self.node_info.port,
            message_id=id,
            recipient_key=recipient_key,
        )
        listing.save()
        logging.debug('Received new message listing %u from %s' % (id, self.node_info.get_name()))

    def unregisterMessageListing(self, id):
        # TODO: verify node IP
        MessageListing.objects.filter(
            node_host=self.node_info.host,
            node_port=self.node_info.port,
            message_id=id,
        ).delete()
        logging.debug('Removed message listing %u by %s' % (id, self.node_info.get_name()))

    def getAuthChallenge(self, publicKey):
        self.auth_public_key = publicKey
        self.auth_public_key_hash = md5_crypt.encrypt(self.auth_public_key, salt='').encode('base64')
        self.auth_complete = False
        return crypto.encrypt_rsa(self.auth_challenge, crypto.load_public_key(publicKey)).encode('base64')

    def confirmAuth(self, response):
        self.auth_complete = response.decode('base64') == self.auth_challenge
        if self.auth_complete:
            logging.debug('Client signed in successfully')
        else:
            logging.debug('Client failed to confirm identity')
        return 1 if self.auth_complete else 0

    def getListings(self):
        if not self.auth_complete:
            return []
        result = []
        for listing in MessageListing.objects.filter(recipient_key_hash=self.auth_public_key_hash).all():
            l = AtlasListing()
            l.node = AtlasNodeInfo()
            l.node.host = listing.node_host
            l.node.port = listing.node_port
            l.id = listing.message_id
            result.append(l)
        return result

    def hasMessage(self, id):
        return 1 if Message.objects.filter(id=id).exists() else 0

    def retrieveMessage(self, id):
        if not self.auth_complete:
            return None
        
        try:
            message = Message.objects.get(id=id)
        except:
            return None
        
        if self.auth_public_key != message.recipient_key:
            return None
        
        result = AtlasMessage()
        result.data = message.data

        for client in atlasnode.nodes.connect_all():
            client.client.unregisterMessageListing(message.id)
        message.delete()

        return result

    def release(self):
        pass
