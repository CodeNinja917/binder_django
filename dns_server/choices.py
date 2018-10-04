# coding: utf-8


class ChoicesClassMeta(type):
    def __new__(cls, name, bases, attrs):
        opt_class = attrs.get('opts', None)
        '''merge opts from parents'''
        if not opt_class:
            opt_class = cls.new_opts_cls()
        for base_cls in bases:
            base_opt_cls = getattr(base_cls, 'opts', None)
            if base_opt_cls:
                for attr in dir(base_opt_cls):
                    if not attr.startswith('__'):
                        setattr(opt_class, attr, getattr(base_opt_cls, attr))

        assert opt_class is not None, (
            "opts class must be defined in class or it's parents")
        choices = []
        opt_values = []
        for attr in dir(opt_class):
            if not attr.startswith('__'):
                attr_key = getattr(opt_class, attr)
                choices.append((attr_key, attr))
                opt_values.append(attr)
        attrs['choices'] = choices
        attrs['opt_values'] = opt_values
        return super(ChoicesClassMeta, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def new_opts_cls():
        class opts:
            pass
        return opts


class AlgorithmChoice(metaclass=ChoicesClassMeta):
    class opts:
        HMAC_MD5 = 'HMAC-MD5.SIG-ALG.REG.INT'
        HMAC_SHA1 = 'hmac-sha1'
        HMAC_SHA224 = 'hmac-sha224'
        HMAC_SHA256 = 'hmac-sha256'
        HMAC_SHA384 = 'hmac-sha384'
        HMAC_SHA512 = 'hmac-sha512'


class ClientUpdateTypeChoice(metaclass=ChoicesClassMeta):
    class opts:
        ZONE = 'ZONE'  # 客户端可以更新任何标志及整个Zone
        HOST = 'HOST'  # 客户端仅可以针对它的域名进行更新
