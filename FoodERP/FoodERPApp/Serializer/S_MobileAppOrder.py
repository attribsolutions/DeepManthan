from ..models import *
from rest_framework import serializers
from ..Serializer.S_Routes import  *

class RetailerAddPartyPrefixsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyPrefixs
        fields = ['Orderprefix', 'Invoiceprefix', 'Grnprefix', 'Receiptprefix','Challanprefix','WorkOrderprefix','MaterialIssueprefix','Demandprefix','IBChallanprefix','IBInwardprefix','PurchaseReturnprefix','Creditprefix','Debitprefix']
        
class RetailerAddAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['Address', 'FSSAINo','FSSAIExipry','IsDefault']  
        
class RetailerAddPartySubPartySerializer(serializers.ModelSerializer):
    class Meta:
        model =MC_PartySubParty
        fields =['Party','Route','CreatedBy','UpdatedBy']


class RetailerAddFromMobileAppSerializer(serializers.ModelSerializer):
    PartyAddress = RetailerAddAddressSerializer(many=True)
    PartyPrefix = RetailerAddPartyPrefixsSerializer(many=True)
    PartySubParty = RetailerAddPartySubPartySerializer(many=True)
    class Meta:
        model =  M_Parties
        fields = '__all__'
        
    def create(self, validated_data):
        PartyAddress_data = validated_data.pop('PartyAddress')
        PartyPrefix_data = validated_data.pop('PartyPrefix')
        PartySubPartys=validated_data.pop('PartySubParty')
        PartyID= M_Parties.objects.create(**validated_data)
        
        for PartyAddress in PartyAddress_data:
            Party = MC_PartyAddress.objects.create(Party=PartyID, **PartyAddress) 

        for PartyPrefix in PartyPrefix_data:
            Partyprefixx = MC_PartyPrefixs.objects.create(Party=PartyID, **PartyPrefix) 
        
        for PartySubParty in PartySubPartys:
            PartySubParty=MC_PartySubParty.objects.create(SubParty=PartyID, **PartySubParty)         
    
        return PartyID