# coding: utf-8


class KeyringException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def get_msg(self):
        return self.msg
