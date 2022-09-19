from dataclasses import fields
from ..models import *
from rest_framework import serializers


class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartyType
        fields = '__all__'


class PartyTypeSerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    IsSCM = serializers.BooleanField()
    IsDivision = serializers.BooleanField()

   