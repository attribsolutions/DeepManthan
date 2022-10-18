from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *
from .S_Items import * 

class MC_PartyItemSerializer(serializers.ModelSerializer):
    Item = ItemSerializerSecond()
    class Meta:
        model =  MC_PartyItems
        fields = '__all__' 