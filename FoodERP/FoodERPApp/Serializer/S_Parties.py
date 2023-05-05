from ..models import *
from rest_framework import serializers

class PartiesSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email']       
        
class DivisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Parties
        fields = ['id','Name']
         
class PartySubPartySerializer2(serializers.ModelSerializer):
    Party = DivisionsSerializer()
    class Meta:
        model = MC_PartySubParty
        fields = ['Party']
              
    
class PartyPrefixsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyPrefixs
        fields = ['Orderprefix', 'Invoiceprefix', 'Grnprefix', 'Receiptprefix','Challanprefix','WorkOrderprefix','MaterialIssueprefix','Demandprefix','IBChallanprefix','IBInwardprefix']

# class PartyAddressSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField()
#     class Meta:
#         model = MC_PartyAddress
#         fields = ['id', 'Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument']  

                     
class PartyAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = MC_PartyAddress
        fields = ['Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument']  
class MC_PartySubPartySerializer(serializers.ModelSerializer):
    class Meta:
        model =MC_PartySubParty
        fields =['Party','CreatedBy','UpdatedBy']

class M_PartiesinstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Parties
        fields = ['id']       

class M_PartiesSerializer(serializers.ModelSerializer):
    PartyAddress = PartyAddressSerializer(many=True)
    PartyPrefix = PartyPrefixsSerializer(many=True)
    PartySubParty = MC_PartySubPartySerializer(many=True)
    class Meta:
        model =  M_Parties
        fields = '__all__'
        
        
    def create(self, validated_data):
        PartyType = validated_data.get('PartyType')
        PartyAddress_data = validated_data.pop('PartyAddress')
        PartyPrefix_data = validated_data.pop('PartyPrefix')
        PartySubPartys=validated_data.pop('PartySubParty')
        PartyID= M_Parties.objects.create(**validated_data)
        
        for PartyAddress in PartyAddress_data:
            Party = MC_PartyAddress.objects.create(Party=PartyID, **PartyAddress) 

        for PartyPrefix in PartyPrefix_data:
            Partyprefixx = MC_PartyPrefixs.objects.create(Party=PartyID, **PartyPrefix) 
        
        
        query=M_PartyType.objects.filter(id=PartyType.id).values('IsVendor')

        if query[0]['IsVendor'] == True:
            for PartySubParty in PartySubPartys:
                subparty = PartySubParty.pop('Party')
                PartySubParty=MC_PartySubParty.objects.create(Party=PartyID,SubParty=subparty, **PartySubParty)
        else:
            
            for PartySubParty in PartySubPartys:
                PartySubParty=MC_PartySubParty.objects.create(SubParty=PartyID, **PartySubParty)         
    
        return PartyID
    
    def update(self, instance, validated_data):
        instance.Name = validated_data.get(
            'Name', instance.Name)
        instance.PriceList = validated_data.get(
            'PriceList', instance.PriceList)
        instance.PartyType = validated_data.get(
            'PartyType', instance.PartyType)
        instance.Company = validated_data.get(
            'Company', instance.Company)
        instance.Email = validated_data.get(
            'Email', instance.Email)
        instance.MobileNo = validated_data.get(
            'MobileNo', instance.MobileNo)
        instance.AlternateContactNo = validated_data.get(
            'AlternateContactNo', instance.AlternateContactNo)
        instance.State = validated_data.get(
            'State', instance.State)
        instance.District = validated_data.get(
            'District', instance.District)
        instance.Taluka = validated_data.get(
            'Taluka', instance.Taluka)
        instance.City = validated_data.get(
            'City', instance.City)
        instance.SAPPartyCode = validated_data.get(
            'SAPPartyCode', instance.SAPPartyCode)
        instance.GSTIN = validated_data.get(
            'GSTIN', instance.GSTIN)
        instance.PAN = validated_data.get(
            'PAN', instance.PAN)
        instance.IsDivision = validated_data.get(
            'IsDivision', instance.IsDivision)
        instance.District = validated_data.get(
            'District', instance.District)
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)
        
        instance.MkUpMkDn = validated_data.get(
            'MkUpMkDn', instance.MkUpMkDn)
            
        instance.save()   
        
        for a in instance.PartyPrefix.all():
            a.delete() 
        
        for a in instance.PartySubParty.all():
            a.delete()       
            
        for PartyAddress_data in validated_data['PartyAddress']:
            Party = MC_PartyAddress.objects.filter(id=PartyAddress_data['id'],Party=instance).update(Address=PartyAddress_data['Address'],FSSAINo=PartyAddress_data['FSSAINo'],FSSAIExipry=PartyAddress_data['FSSAIExipry'],PIN=PartyAddress_data['PIN'],IsDefault=PartyAddress_data['IsDefault'],fssaidocument=PartyAddress_data['fssaidocument'])

        for PartyPrefixs_data in validated_data['PartyPrefix']:
            Party = MC_PartyPrefixs.objects.create(Party=instance, **PartyPrefixs_data)
        
        query=M_PartyType.objects.filter(id=instance.PartyType).values('IsVendor')
        if query[0]['IsVendor'] == True:
            for PartySubParty in validated_data['PartySubParty']:
                subparty = PartySubParty.pop('Party')
                PartySubParty=MC_PartySubParty.objects.create(Party=instance,SubParty=subparty, **PartySubParty)  
        else:   
            for PartySubParty in validated_data['PartySubParty']:
                PartySubParty=MC_PartySubParty.objects.create(SubParty=instance, **PartySubParty)     
                        
        return instance
            
class M_PartiesSerializer1(serializers.Serializer):

    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    PartyType_id = serializers.IntegerField( )
    PartyTypeName = serializers.CharField(max_length=500)
    PriceList_id =  serializers.IntegerField()
    PriceListName = serializers.CharField(max_length=500)
    Company_id =  serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=500)
    Email = serializers.EmailField(max_length=200)
    Address = serializers.CharField(max_length=500)
    MobileNo=serializers.IntegerField()
    AlternateContactNo=serializers.CharField(max_length=500)
    PIN = serializers.CharField(max_length=500)
    State_id = serializers.IntegerField()
    StateName = serializers.CharField(max_length=500)
    District_id = serializers.IntegerField()
    DistrictName = serializers.CharField(max_length=500)
    Taluka = serializers.IntegerField ()
    City = serializers.IntegerField()
    SAPPartyCode = serializers.CharField(max_length = 500)
    GSTIN =  serializers.CharField(max_length=500)
    PAN =  serializers.CharField(max_length=500)
    FSSAINo = serializers.CharField(max_length=500)
    FSSAIExipry = serializers.DateField()
    isActive =  serializers.BooleanField()
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField()

    
class PartyAddressSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['id','Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault','fssaidocument'] 

class DistrictSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_PriceList
        fields = ['id','Name']
        
class StateSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_States
        fields = ['id','Name'] 
        
class CompanySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  C_Companies
        fields = ['id','Name']
        
class PartyTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_PartyType
        fields = ['id','Name']

class PriceListSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_PriceList
        fields = ['id','Name']                           
    
class M_PartiesSerializerSecond(serializers.ModelSerializer):
    PartyAddress = PartyAddressSerializerSecond(many=True)
    District= DistrictSerializerSecond()
    State= StateSerializerSecond()
    Company = CompanySerializerSecond()
    PartyType = PartyTypeSerializerSecond()
    PriceList=PriceListSerializerSecond()
    PartyPrefix = PartyPrefixsSerializer(many=True)
    class Meta:
        model =  M_Parties
        fields = '__all__'
        

class M_PartiesSerializerThird(serializers.Serializer):
    
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    ManagementEmpparty__Party_id = serializers.IntegerField()
    

class M_PartiesSerializerFourth(serializers.ModelSerializer):
   
    District= DistrictSerializerSecond()
    State= StateSerializerSecond()
    PartyType = PartyTypeSerializerSecond()
    class Meta:
        model =  M_Parties
        fields = '__all__'    
    
    
   
   
  



  