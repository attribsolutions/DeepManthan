from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *

  
class PartySubpartySerializer(serializers.ModelSerializer):
    class Meta :
        model= MC_PartySubParty
        fields = '__all__'  

