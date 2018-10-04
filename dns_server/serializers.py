# coding: utf-8

from rest_framework import serializers
from .models import Server
from .models import Key
from .models import Zone
from .models import Record


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = '__all__'


class ZoneSerializer(serializers.ModelSerializer):
    # server = serializers.SerializerMethodField()

    def get_server(self, obj):
        try:
            server_info = {
                'id': obj.server.id,
                'name': obj.server.name,
            }
        except AttributeError:
            server_info = {}

        return server_info

    class Meta:
        model = Zone
        fields = ['id', 'view_name', 'zone_name', 'zone_class',
                  'zone_serial', 'created_time', 'description', 'server']


class RecordSerializer(serializers.ModelSerializer):
    # zone = serializers.SerializerMethodField()

    def get_zone(self, obj):
        zone_info = {
            'id': obj.zone.id,
            'name': obj.zone.zone_name
        }

        return zone_info

    class Meta:
        model = Record
        fields = ['id', 'name', 'ttl', 'rr_class', 'rr_type',
                  'rr_data', 'created_time', 'description', 'zone']
