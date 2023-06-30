from rest_framework import serializers
from ..models import *

class PartySubPartySerializer(serializers.ModelSerializer):
    class Meta :
        model= MC_PartySubParty
        fields = '__all__'

class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= M_PartyType
        fields = '__all__'

class Partyaddress(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['FSSAINo','FSSAIExipry','IsDefault']

    def to_representation(self, instance):
            # get representation from ModelSerializer
        ret = super(Partyaddress, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("FSSAINo", None):
            ret["FSSAINo"] = None

        if not ret.get("FSSAIExipry", None):
            ret["FSSAIExipry"] = None
        return ret  

class PartySerializer(serializers.ModelSerializer):
    PartyType=PartyTypeSerializer(read_only=True)
    PartyAddress=Partyaddress(many=True)
    PartySubParty=PartySubPartySerializer(read_only=True) 
    class Meta:
        model =  M_Parties
        fields = ['id','Name','PartyType','GSTIN','PartyAddress','PartySubParty','PAN']
        
class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Routes
        fields = '__all__'        
  
class PartySubpartySerializerSecond(serializers.ModelSerializer):
    SubParty = PartySerializer(read_only=True)
    Party = PartySerializer(read_only=True)
    Route = RouteSerializer(read_only=True)
    class Meta :
        model= MC_PartySubParty
        fields = '__all__'
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(PartySubpartySerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Route", None):
            ret["Route"] = {"id": None, "Name": None}

        
        return ret          
          

class PartySubPartySerializerGETList(serializers.Serializer):
    
    Party_id = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    Subparty = serializers.IntegerField() 
    

class PartySubPartyCreditlimit(serializers.ModelSerializer):
    SubParty = PartySerializer(read_only=True)
    Party = PartySerializer(read_only=True)
    class Meta :
        model= MC_PartySubParty
        fields = ['id','Party','SubParty','Creditlimit']
        
    

