from django.db import models
from .choices import AlgorithmChoice
from .choices import ClientUpdateTypeChoice
from .exceptions import KeyringException
from binder.settings import DNS

from cryptography.fernet import Fernet, InvalidToken
from fabric import Connection
import time
import dns
import dns.zone
import dns.query
import dns.update
import dns.tsigkeyring
from pybindxml import reader

# Create your models here.


class Server(models.Model):
    name = models.CharField(max_length=128, unique=True, null=True)
    ip_address = models.GenericIPAddressField()
    dns_port = models.IntegerField(default=53)
    statistics_port = models.IntegerField(default=8053)
    default_transfer_key = models.ForeignKey(
        'Key', related_name='server',
        blank=True, null=True, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=2048, default='')

    def list_zones(self):
        zones = reader.BindXmlReader(
            host=self.ip_address, port=self.statistics_port)
        zones.get_stats()

        for name, view in zones.stats.zone_stats.items():
            for view_name, view_info in view.items():
                if name.lower().endswith('arpa') or\
                        'localhost' in name.lower():
                    continue
                zone_obj, _ = Zone.objects.get_or_create(zone_name=name)
                zone_obj.server = self
                zone_obj.view_name = view_name
                zone_obj.zone_serial = view_info['serial']
                zone_obj.save()

    class Meta:
        ordering = ('-id', )


class Key(models.Model):
    name = models.CharField(max_length=32, unique=True)
    algorithm = models.CharField(
        max_length=32, choices=AlgorithmChoice.choices,
        default=AlgorithmChoice.opts.HMAC_SHA1)
    passwd_len = models.IntegerField(default=512)
    update_type = models.CharField(
        max_length=16, choices=ClientUpdateTypeChoice.choices,
        default=ClientUpdateTypeChoice.opts.HOST)
    data = models.CharField(max_length=255, default='')
    created_time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=2048, default='')

    def save(self, *args, **kwargs):
        f = Fernet(DNS['FERNET_KEY'])
        if isinstance(self.data, bytes):
            self.data = f.encrypt(self.data).decode('utf-8')
        else:
            self.data = f.encrypt(self.data.encode('utf-8')).decode('utf-8')

        super(Key, self).save(*args, **kwargs)

    def create_keyring(self):
        if self.name is None:
            return None

        key_data = self.decrypt_keydata()
        kerying = dns.tsigkeyring.from_text({self.name: key_data})

        return kerying

    def decrypt_keydata(self):
        f = Fernet(DNS['FERNET_KEY'])
        try:
            if isinstance(self.data, bytes):
                data = f.decrypt(self.data)
            else:
                data = f.decrypt(self.data.encode('utf-8'))
        except InvalidToken:
            raise KeyringException('invalid data for dns key')

        return data.decode('utf-8')

    class Meta:
        ordering = ('-id',)


class Zone(models.Model):
    server = models.ForeignKey(
        Server, related_name='zone', blank=True,
        null=True, on_delete=models.CASCADE)
    view_name = models.CharField(max_length=32, default='_default')
    zone_name = models.CharField(max_length=256, null=True)
    zone_class = models.CharField(max_length=256, default='IN')
    zone_serial = models.CharField(max_length=64, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=2048, default='')

    def save(self, *args, **kwargs):
        self.zone_serial = int(time.time())
        super(Zone, self).save(*args, **kwargs)

    def list_records(self):
        try:
            transfer_key = self.server.default_transfer_key
        except Key.DoesNotExist:
            keyring = None
            algorithm = None
        else:
            keyring = transfer_key.create_keyring()
            algorithm = transfer_key.algorithm

        zone = dns.zone.from_xfr(dns.query.xfr(
            self.server.ip_address, self.zone_name,
            port=self.server.dns_port, keyring=keyring,
            keyalgorithm=algorithm))
        names = zone.nodes.keys()
        for cur_name in names:
            cur_record = zone[cur_name].to_text(cur_name)
            for record_info in cur_record.split('\n'):
                cur_record = record_info.split(' ')
                record_obj, _ = Record.objects.get_or_create(
                    name=cur_record[0])
                record_obj.ttl = cur_record[1]
                record_obj.rr_class = cur_record[2]
                record_obj.rr_type = cur_record[3]
                record_obj.rr_data = cur_record[4]
                record_obj.zone = self
                record_obj.save()

    def add_zone(self):
        zone_content = DNS['ZONE_TEMPLATE'].format(
            email='admin.' + self.zone_name,
            serial=self.zone_serial
        )
        con = Connection(DNS['MASTER_SERVER'], connect_kwargs={
                         'key_filename': '/root/.ssh/id_rsa'})
        con.run("echo '{}' > /var/named/data/db.{}".format(
            zone_content, self.zone_name))
        add_zone_cmd = (
            "/usr/sbin/rndc addzone %(zone_name)s IN %(view_name)s "
            "\'{type master;file \"data/db.%(zone_name)s\"; allow-update "
            "{ 192.168.137.134; key web;};};\'")
        con.run(add_zone_cmd %
                {'zone_name': self.zone_name, 'view_name': self.view_name})
        con.run('/usr/sbin/rndc reload')
        con.close()

    def delete_zone(self):
        con = Connection(DNS['MASTER_SERVER'], connect_kwargs={
            'key_filename': '/root/.ssh/id_rsa'})
        con.run('/usr/sbin/rndc delzone {}'.format(self.zone_name))
        con.close()

    class Meta:
        ordering = ('-id',)


class Record(models.Model):
    zone = models.ForeignKey(
        Zone, related_name='record', blank=True,
        null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=True)
    ttl = models.IntegerField(default=3600)
    rr_class = models.CharField(max_length=64, default='IN')
    rr_type = models.CharField(max_length=16, default='A')
    rr_data = models.CharField(max_length=256, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=2048, default='')

    def add_record(self):
        try:
            transfer_key = self.zone.server.default_transfer_key
        except Key.DoesNotExist:
            keyring = None
            algorithm = None
        else:
            keyring = transfer_key.create_keyring()
            algorithm = transfer_key.algorithm

        dns_update = dns.update.Update(
            self.zone.zone_name, keyring=keyring, keyalgorithm=algorithm)
        dns_update.replace(self.name, self.ttl, self.rr_type, self.rr_data)
        resp = dns.query.tcp(
            dns_update, self.zone.server.ip_address,
            port=self.zone.server.dns_port)
        if resp.rcode() != dns.rcode.NOERROR:
            self.delete()

    def update_record(self):
        self.add_record()

    def delete_record(self):
        try:
            transfer_key = self.zone.server.default_transfer_key
        except Key.DoesNotExist:
            keyring = None
            algorithm = None
        else:
            keyring = transfer_key.create_keyring()
            algorithm = transfer_key.algorithm

        dns_update = dns.update.Update(
            self.zone.zone_name, keyring=keyring, keyalgorithm=algorithm)
        dns_update.delete(self.name)
        resp = dns.query.tcp(
            dns_update, self.zone.server.ip_address,
            port=self.zone.server.dns_port)
        if resp.rcode() == dns.rcode.NOERROR:
            pass
        else:
            print(resp.rcode())

    class Meta:
        ordering = ('-id',)
