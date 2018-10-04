# coding: utf-8
from pybindxml import reader


class Zone(object):
    def list_zones(self, ip_address, statistics_port):
        zones = reader.BindXmlReader(
            host=ip_address, port=statistics_port)
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


class Record(object):
    pass
