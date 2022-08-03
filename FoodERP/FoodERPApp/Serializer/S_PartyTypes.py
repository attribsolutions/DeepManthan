from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *

# Get ALL Method
class PartyTypesSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = M_PartyType
        fields = '__all__'

class PartyTypesSerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    DivisionType_id = serializers.IntegerField()
    DivisionTypeName = serializers.CharField(max_length=100)
      