from django.forms import SlugField
from rest_framework import serializers
from ..models import  *

class SubPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = '__all__' 
        

class PartyWiseSerializer(serializers.ModelSerializer):
    SubParty= SubPartySerializer(read_only=True)
    class Meta:
        model =   MC_PartySubParty
        fields = '__all__'
        
