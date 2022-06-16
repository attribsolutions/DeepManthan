from ..models import *
from rest_framework import serializers

class ItemsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ItemsGroup
        fields = '__all__'