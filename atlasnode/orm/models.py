import os
from passlib.hash import md5_crypt

from django.db import models


class Node (models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    
    def get_name(self):
        return '%s:%i' % (self.host, self.port)

    @staticmethod
    def find(info=None, descriptor=None):
        if info:
            q = {'host': info.host, 'port': info.port}
        elif descriptor:
            q = {'host': descriptor[0], 'port': descriptor[1]}
        else:
            return None
        if Node.objects.filter(**q).exists():
            return Node.objects.get(**q)
        return None


class Message (models.Model):
    data = models.TextField()
    recipient_challenge = models.TextField()
    recipient_key_hash = models.CharField(max_length=255, db_index=True)
    recipient_key = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.recipient_key_hash:
            self.recipient_key_hash = md5_crypt.encrypt(self.recipient_key, salt='').encode('base64')
        if not self.recipient_challenge:
            self.recipient_challenge = os.urandom(1024).encode('base64')
        models.Model.save(self, *args, **kwargs)


class MessageListing (models.Model):
    node_host = models.CharField(max_length=255)
    node_port = models.IntegerField()
    message_id = models.IntegerField(db_index=True)
    recipient_key_hash = models.CharField(max_length=255, db_index=True)
    recipient_key = models.TextField()

    def save(self, *args, **kwargs):
        if not self.recipient_key_hash:
            self.recipient_key_hash = md5_crypt.encrypt(self.recipient_key, salt='').encode('base64')
        models.Model.save(self, *args, **kwargs)
