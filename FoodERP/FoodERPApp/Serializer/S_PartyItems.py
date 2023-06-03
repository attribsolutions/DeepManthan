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
    Item = M_ItemsSerializer01(read_only=True)
    Party = DivisionsSerializer(read_only=True)
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

class MC_PartyItemSerializerSingleGet(serializers.Serializer):
    id = serializers.IntegerField()
    Name=serializers.CharField(max_length=500)
    Party_id = serializers.IntegerField()
    PartyName=serializers.CharField(max_length=500)
    GroupTypeName=serializers.CharField(max_length=500)
    GroupName=serializers.CharField(max_length=500)
    SubGroupName=serializers.CharField(max_length=500)
  
    
     
class MC_PartyItemListSerializer(serializers.Serializer):
    Party_id = serializers.IntegerField()
    Name=serializers.CharField(max_length=500)
    Item_id = serializers.IntegerField()
    Total = serializers.IntegerField()
    
    
        
     
        
    
               