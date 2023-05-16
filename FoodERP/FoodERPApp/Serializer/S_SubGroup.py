from rest_framework import serializers
from ..models import *
# Post and Put Methods Serializer

class SubGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_SubGroup
        fields = '__all__'

# Get ALL SubGroup,Get Single SubGroup,Get SubGroup On Group Methods Serializers


class GroupSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_Group
        fields = ['id','Name']

class SubGroupSerializerSecond(serializers.ModelSerializer):
    Group = GroupSerializerSecond(read_only=True)
    class Meta:
        model = MC_SubGroup
        fields = '__all__'      