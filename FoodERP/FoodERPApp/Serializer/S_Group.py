from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Group
        fields = '__all__'

# Get ALL Group,Get Single Group,Get Group On GroupType Methods Serializers

class GroupTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_GroupType
        fields = '__all__'

class GroupSerializerSecond(serializers.ModelSerializer):
    GroupType = GroupTypeSerializerSecond(read_only=True)
    class Meta:
        model = M_Group
        fields = '__all__'      