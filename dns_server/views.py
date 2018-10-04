from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Server
from .models import Key
from .models import Zone
from .models import Record
from .serializers import ServerSerializer
from .serializers import KeySerializer
from .serializers import ZoneSerializer
from .serializers import RecordSerializer
# Create your views here.


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    @action(methods=['get'], detail=True, url_path='sync_server_zone')
    def sync_server_zone(self, request, pk=None, *args, **kwargs):
        server_obj = self.queryset.get(id=pk)
        server_obj.list_zones()

        return Response(data='ok', status=status.HTTP_200_OK)


class KeyViewSet(viewsets.ModelViewSet):
    queryset = Key.objects.all()
    serializer_class = KeySerializer


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=True, url_path='sync_zone_records')
    def sync_zone_records(self, request, pk=None, *args, **Kwargs):
        zone_obj = self.queryset.get(id=pk)
        zone_obj.list_records()

        return Response(data='ok', status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.add_zone()

    def perform_destroy(self, instance):
        instance.delete_zone()
        instance.delete()


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.add_record()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.update_record()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete_record()
        # instance.delete()
