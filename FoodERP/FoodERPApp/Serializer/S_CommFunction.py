
from rest_framework import serializers

from ..models import MC_ItemUnits


class ItemUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemUnits
        fields = '__all__'