from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers
from ..models import *
from .S_Items import *
from .S_Parties import *

class MC_PartyItemSerializerSecond(serializers.ModelSerializer):
    Item = ItemSerializerSecond()
    class Meta:
        model =  MC_PartyItems
        fields = '__all__' 

class MC_PartyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MC_PartyItems
        fields = '__all__'   

class MC_PartyItemSerializerThird(serializers.ModelSerializer):
    Item = ItemSerializerSecond()
    Party = M_PartiesSerializerSecond()
    class Meta:
        model =  MC_PartyItems
        fields = '__all__' 
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(MC_PartyItemSerializerThird, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Item", None):
            ret["Item"] = {"id": None, "Name": None}  
       
        if not ret.get("Party", None):
            ret["Party"] = {"id": None, "Name": None}  
        return ret
  
               