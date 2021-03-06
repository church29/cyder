from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicInterfaceAV)


class DynamicInterfaceAVSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    entity = serializers.HyperlinkedRelatedField(
        view_name='api-dhcp-dynamicinterface-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = DynamicInterfaceAV



class DynamicInterfaceAVViewSet(api.CommonDHCPViewSet):
    model = DynamicInterfaceAV
    serializer_class = DynamicInterfaceAVSerializer


class DynamicInterfaceNestedAVSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-dynamicinterface_attributes-detail')

    class Meta:
        model = DynamicInterfaceAV
        fields = api.NestedAVFields


class DynamicInterfaceSerializer(serializers.ModelSerializer):
    dynamicinterfaceav_set = DynamicInterfaceNestedAVSerializer(
        many=True, required=False)
    system = serializers.HyperlinkedRelatedField(
        view_name='api-core-system-detail')
    range = serializers.HyperlinkedRelatedField(
        view_name='api-dhcp-range-detail')
    ctnr = serializers.HyperlinkedRelatedField(
        view_name='api-core-ctnr-detail')
    workgroup = serializers.HyperlinkedRelatedField(
        view_name='api-dhcp-workgroup-detail', required=False)

    class Meta(api.CommonDHCPMeta):
        model = DynamicInterface
        depth = 1


class DynamicInterfaceViewSet(api.CommonDHCPViewSet):
    model = DynamicInterface
    serializer_class = DynamicInterfaceSerializer
    avmodel = DynamicInterfaceAV
    avmodel_entity = 'dynamic_interface'
