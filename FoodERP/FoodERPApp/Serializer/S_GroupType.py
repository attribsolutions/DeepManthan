from ..models import *
from rest_framework import serializers

class GroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_GroupType
        fields = '__all__'