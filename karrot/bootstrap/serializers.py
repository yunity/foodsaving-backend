from rest_framework import serializers

from karrot.groups.serializers import GroupPreviewSerializer
from karrot.userauth.serializers import AuthUserSerializer


class GeoSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class BootstrapSerializer(serializers.Serializer):
    user = AuthUserSerializer()
    geoip = GeoSerializer()
    groups = GroupPreviewSerializer(many=True)
