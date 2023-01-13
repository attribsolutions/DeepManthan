from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Parties
        fields = '__all__'
  
class PartySubpartySerializerSecond(serializers.ModelSerializer):
    SubParty = PartySerializer(read_only=True)
    Party = PartySerializer(read_only=True)
    class Meta :
        model= MC_PartySubParty
        fields = '__all__'  

class PartySubPartySerializer(serializers.ModelSerializer):
    class Meta :
        model= MC_PartySubParty
        fields = '__all__'  
