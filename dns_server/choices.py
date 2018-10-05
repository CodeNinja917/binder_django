# coding: utf-8
from collections import OrderedDict


class BaseChoice(object):
    _attrs = {}

    def __init__(self):
        for value, name in self._attrs.items():
            setattr(self, name, value)

    @property
    def choices(self):
        return self._attrs.items()


class AlgorithmChoice(BaseChoice):
    _attrs = OrderedDict([
        ('HMAC-MD5.SIG-ALG.REG.INT', 'HMAC_MD5'),
        ('hmac-sha1', 'HMAC_SHA1'),
        ('hmac-sha224', 'HMAC_SHA224'),
        ('hmac-sha256', 'HMAC_SHA224'),
        ('hmac-sha384', 'HMAC_SHA256'),
        ('hmac-sha512', 'HMAC_SHA512'),
    ])


class ClientUpdateTypeChoice(BaseChoice):
    _attrs = OrderedDict([
        ('ZONE', 'ZONE'),  # 客户端可以更新任何标志及整个Zone
        ('HOST', 'HOST')   # 客户端仅可以针对它的域名进行更新
    ])


alogrithms = AlgorithmChoice()
client_update_types = ClientUpdateTypeChoice()
