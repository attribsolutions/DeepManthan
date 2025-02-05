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


class RetailerUpdateFormMobileAppAddressSerializer(serializers.ModelSerializer):
    FoodERPRetailerID = serializers.IntegerField()
    class Meta:
        model = MC_PartyAddress
        fields = ['Address', 'FSSAINo', 'FSSAIExipry','FoodERPRetailerID']      
    
class RetailerUpdateFromMobileAppSerializer(serializers.ModelSerializer):
    PartyAddress = RetailerUpdateFormMobileAppAddressSerializer(many=True)
    class Meta:
        model =  M_Parties
        fields = ['id','Name', 'Email', 'MobileNo', 'GSTIN','PAN', 'isActive', 'Latitude','Longitude','PartyAddress'] 
        
        
    def update(self, instance, validated_data):
        instance.Name = validated_data.get(
            'Name', instance.Name)
        instance.Email = validated_data.get(
            'Email', instance.Email)
        instance.MobileNo = validated_data.get(
            'MobileNo', instance.MobileNo)
        instance.GSTIN = validated_data.get(
            'GSTIN', instance.GSTIN)
        instance.PAN = validated_data.get(
            'PAN', instance.PAN)
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)
        instance.Latitude = validated_data.get(
            'Latitude', instance.Latitude)
        instance.Longitude = validated_data.get(
            'Longitude', instance.Longitude)
            
        instance.save()   
        
        for PartyAddress_updatedata in validated_data['PartyAddress']:
            if PartyAddress_updatedata['FoodERPRetailerID'] >0:
                Partyaddress = MC_PartyAddress.objects.filter(Party=PartyAddress_updatedata['FoodERPRetailerID'],IsDefault=1).update(Address=PartyAddress_updatedata['Address'],FSSAINo=PartyAddress_updatedata['FSSAINo'],FSSAIExipry=PartyAddress_updatedata['FSSAIExipry'])
                        
        return instance     