# coding: utf-8
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from ..serializers import ZoneSerializer, ServerSerializer, KeySerializer


class ZoneTestCase(APITestCase):
    data = {
        'view_name': '_default',
        'zone_name': 'test.com',
        'zone_class': 'IN',
        'description': 'ZoneTestCase'
    }

    @classmethod
    def create_test_zone_data(cls):
        serializer = ZoneSerializer(data=cls.data)
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

    def setUp(self):
        user = User.objects.create_user(
            username='admin', password='admin', is_superuser=True)
        user.save()
        ret = self.client.login(username='admin', password='admin')
        self.assertTrue(ret)
        self.server_obj = self.create_test_server_data()

    def test_create_zone(self):
        url = reverse('dns_server:dns-zone-list')
        self.data.update({'server': self.server_obj.id})
        resp = self.client.post(url, self.data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_sync_zone(self):
        url = reverse('dns_server:dns-server-sync-server-zone',
                      kwargs={'pk': self.server_obj.id})
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.data, 'ok')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    '''def test_del_zone(self):
        self.data.update({'server': self.server_obj.id})
        zone_obj = self.create_test_zone_data()
        url = reverse('dns_server:dns-zone-detail', kwargs={'pk': zone_obj.id})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    '''
