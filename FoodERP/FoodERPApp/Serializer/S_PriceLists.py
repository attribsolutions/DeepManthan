from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *

# Get ALL Method
class PriceListSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = M_PriceList
        fields = '__all__'

class PriceListSerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    BasePriceListID = serializers.IntegerField()
    Company_id = serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=100)
    MkUpMkDn = serializers.IntegerField()
    MkUpMkDnName = serializers.CharField(max_length=100)
    PLPartyType_id = serializers.IntegerField()
    PartyTypeName = serializers.CharField(max_length=100)
      