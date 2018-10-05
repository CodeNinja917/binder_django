# coding: utf-8
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Zone
from ..serializers import (
    ZoneSerializer, ServerSerializer, KeySerializer, RecordSerializer)


class ZoneTestCase(APITestCase):
    data = {
        "name": "test",
        "ttl": 3600,
        "rr_class": "IN",
        "rr_type": "A",
        "rr_data": "192.168.137.137",
        "description": "test",
    }

    @classmethod
    def create_test_key_data(cls):
        data = {
            'name': 'web',
            'algorithm': 'HMAC-MD5.SIG-ALG.REG.INT',
            'passwd_len': 128,
            'update_type': 'HOST',
            'data': 'gmP4qpf0T5bkZLRPodruQg=='
        }
        serializer = KeySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    def create_test_server_data(cls):
        key_obj = cls.create_test_key_data()
        data = {
            'name': 'test',
            'ip_address': '192.168.137.136',
            'dns_port': 53,
            'statistics_port': 8053,
            'description': 'test',
            'default_transfer_key': key_obj.id
        }
        serializer = ServerSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    def create_test_zone_data(cls):
        server_obj = cls.create_test_server_data()
        data = {
            'server': server_obj.id,
            'view_name': '_default',
            'zone_name': 'test.com',
            'zone_class': 'IN',
            'description': 'ZoneTestCase'
        }
        serializer = ZoneSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    def create_test_record_data(cls):
        zone_obj = cls.create_test_zone_data()
        data = {
            "name": "test1",
            "ttl": 3600,
            "rr_class": "IN",
            "rr_type": "A",
            "rr_data": "192.168.137.137",
            "description": "test",
            "zone": zone_obj.id
        }
        serializer = RecordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def setUp(self):
        user = User.objects.create_user(
            username='admin', password='admin', is_superuser=True)
        user.save()
        ret = self.client.login(username='admin', password='admin')
        self.assertTrue(ret)

    def test_create_record(self):
        self.zone_obj = self.create_test_zone_data()
        self.data['zone'] = self.zone_obj.id
        url = reverse('dns_server:dns-record-list')
        resp = self.client.post(url, self.data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_update_record(self):
        record_obj = self.create_test_record_data()
        url = reverse('dns_server:dns-record-detail',
                      kwargs={'pk': record_obj.id})
        data = {
            'rr_data': '127.0.0.1'
        }
        resp = self.client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_del_record(self):
        record_obj = self.create_test_record_data()
        url = reverse('dns_server:dns-record-detail',
                      kwargs={'pk': record_obj.id})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
