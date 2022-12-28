
from rest_framework import serializers

from ..models import MC_ItemUnits,M_Units,M_Items


class ItemUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemUnits
        fields = '__all__'

class UnitSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']

class ItemSerializerSecond(serializers.ModelSerializer):
    BaseUnitID = UnitSerializerSecond()
    class Meta:
        model = M_Items
        fields='__all__'       