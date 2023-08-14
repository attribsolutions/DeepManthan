from ..models import *
from rest_framework import serializers
from ..Serializer.S_Routes import  *

class PartiesSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email','MobileNo']       

class Partyaddress(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['FSSAINo','FSSAIExipry','IsDefault']        

class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= M_PartyType
        fields = '__all__'

class DivisionsSerializer(serializers.ModelSerializer):
    PartyType=PartyTypeSerializer(read_only=True)
    PartyAddress=Partyaddress(many=True)
    class Meta:
        model =  M_Parties
        fields = ['id','Name','PartyType','GSTIN','PartyAddress','SAPPartyCode']
        
    # def to_representation(self, instance):
    #     # get representation from ModelSerializer
    #     ret = super(DivisionsSerializer, self).to_representation(instance)
    #     # if parent is None, overwrite
    #     if not ret.get("SAPPartyCode", None):
    #         ret["SAPPartyCode"] =instance.SAPPartyCodes
    #     return ret     
        
        
         
class PartySubPartySerializer2(serializers.ModelSerializer):
    Party = DivisionsSerializer()
    Route = RoutesSerializer()
    class Meta:
        model = MC_PartySubParty
        fields = ['Party','SubParty','Creditlimit','Route','Distance']
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(PartySubPartySerializer2, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Route", None):
            ret["Route"] = {"id": None, "Name": None}
           
        return ret          
    
class PartyPrefixsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyPrefixs
        fields = ['Orderprefix', 'Invoiceprefix', 'Grnprefix', 'Receiptprefix','Challanprefix','WorkOrderprefix','MaterialIssueprefix','Demandprefix','IBChallanprefix','IBInwardprefix','PurchaseReturnprefix']
        
class PartyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['Address', 'FSSAINo', 'PIN', 'IsDefault', 'fssaidocument']  
        
class MC_PartySubPartySerializer(serializers.ModelSerializer):
    class Meta:
        model =MC_PartySubParty
        fields =['Party','Route','CreatedBy','UpdatedBy']

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
    CityName = serializers.CharField(max_length=500)
    City_id = serializers.IntegerField()
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
        
class CitiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_Cities
        fields = ['id','Name']
    
class DistrictSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_Districts
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
    City=CitiesSerializerSecond()
    District= DistrictSerializerSecond()
    State= StateSerializerSecond()
    Company = CompanySerializerSecond()
    PartyType = PartyTypeSerializerSecond()
    PriceList=PriceListSerializerSecond()
    PartyPrefix = PartyPrefixsSerializer(many=True)

    class Meta:
        model =  M_Parties
        fields = '__all__'
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(M_PartiesSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Latitude", None):
            ret["Latitude"] = None  
        if not ret.get("Longitude", None):
            ret["Longitude"] = None    
        return ret    

class M_PartiesSerializerThird(serializers.Serializer):
    
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    ManagementEmpparty__Party_id = serializers.IntegerField()
    

class M_PartiesSerializerFourth(serializers.Serializer):
    id = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    PartyTypeName = serializers.CharField(max_length=500)
    StateName = serializers.CharField(max_length=500)
    DistrictName = serializers.CharField(max_length=500)
    PartyID = serializers.IntegerField()
    
    
    # City=CitiesSerializerSecond()
    # District= DistrictSerializerSecond()
    # State= StateSerializerSecond()
    # PartyType = PartyTypeSerializerSecond()
    # class Meta:
    #     model =  M_Parties
    #     fields = '__all__'
        
        
####################################################################################################################     
        
          
class UpdatePartyPrefixsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyPrefixs
        fields = ['Orderprefix', 'Invoiceprefix', 'Grnprefix', 'Receiptprefix','Challanprefix','WorkOrderprefix','MaterialIssueprefix','Demandprefix','IBChallanprefix','IBInwardprefix']
        
class UpdatePartyAddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = MC_PartyAddress
        fields = ['id','Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument']  
        
class UpdateMC_PartySubPartySerializer(serializers.ModelSerializer):
    
    class Meta:
        model =MC_PartySubParty
        fields =['Party','Route','CreatedBy','UpdatedBy']


class UpdateM_PartiesSerializer(serializers.ModelSerializer):
    PartyAddress = UpdatePartyAddressSerializer(many=True)
    PartyPrefix = UpdatePartyPrefixsSerializer(many=True)
    PartySubParty = UpdateMC_PartySubPartySerializer(many=True)
    class Meta:
        model =  M_Parties
        fields = '__all__'
        
        
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
        instance.Latitude = validated_data.get(
            'Latitude', instance.Latitude)
        instance.Longitude = validated_data.get(
            'Longitude', instance.Longitude)
            
        instance.save()   
        
        for a in instance.PartyPrefix.all():
            a.delete() 
        
        for PartyPrefixs_data in validated_data['PartyPrefix']:
            Partyprefix = MC_PartyPrefixs.objects.create(Party=instance, **PartyPrefixs_data)
             
        for PartyAddress_updatedata in validated_data['PartyAddress']:
            
            if PartyAddress_updatedata['id'] >0:
                Partyaddress = MC_PartyAddress.objects.filter(id=PartyAddress_updatedata['id']).update(Address=PartyAddress_updatedata['Address'],FSSAINo=PartyAddress_updatedata['FSSAINo'],FSSAIExipry=PartyAddress_updatedata['FSSAIExipry'],PIN=PartyAddress_updatedata['PIN'],IsDefault=PartyAddress_updatedata['IsDefault'],fssaidocument=PartyAddress_updatedata['fssaidocument'])
            else:
                PartyPrefix_data = PartyAddress_updatedata.pop('id')
                Party = MC_PartyAddress.objects.create(Party=instance, **PartyAddress_updatedata)   
               
            
        query=M_PartyType.objects.filter(id=instance.PartyType.id).values('IsVendor')
       
        if query[0]['IsVendor'] == True:
            for PartySubParty in validated_data['PartySubParty']:
                query =MC_PartySubParty.objects.filter(Party=instance,SubParty=PartySubParty['Party']).delete()
                PartySubParty=MC_PartySubParty.objects.create(Party=instance,SubParty=PartySubParty['Party'], **PartySubParty)  
        else: 
          
            for PartySubParty in validated_data['PartySubParty']:
                query =MC_PartySubParty.objects.filter(Party=PartySubParty['Party'],SubParty=instance).delete()
                PartySubParty=MC_PartySubParty.objects.create(SubParty=instance, **PartySubParty)     
                        
        return instance        
        
                    

   
  



  