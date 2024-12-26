from ..models import *
from rest_framework import serializers
from ..Serializer.S_Routes import  *

class PartiesSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email','MobileNo','PartyType']       

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
        
class PartySerializer1(serializers.ModelSerializer):    
    class Meta:
        model =  M_Parties
        fields = ['id','Name']        
class PartyaddressSecond(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['Address']
        
class DivisionsSerializerSecond(serializers.ModelSerializer):
    PartyType=PartyTypeSerializer(read_only=True)
    Address = serializers.CharField(source='PartyAddress.first.Address')
    class Meta:
        model =  M_Parties
        fields = ['id', 'Name', 'SAPPartyCode', 'Latitude', 'Longitude', 'MobileNo', 'Address' ,'PartyType']
        
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
        fields = ['Orderprefix', 'Invoiceprefix', 'Grnprefix', 'Receiptprefix','Challanprefix','WorkOrderprefix','MaterialIssueprefix','Demandprefix','IBChallanprefix','IBInwardprefix','PurchaseReturnprefix','Creditprefix','Debitprefix']
        
class PartyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument']  
        
class MC_PartySubPartySerializer(serializers.ModelSerializer):
    class Meta:
        model =MC_PartySubParty
        fields =['Party','Route','CreatedBy','UpdatedBy']

class M_PartiesinstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Parties
        fields = ['id']       

class CSSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_PartyDetails
        fields = ['Cluster', 'SubCluster']

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = M_Country
        fields = ['id','Country']

class M_PartiesSerializer(serializers.ModelSerializer):
    PartyAddress = PartyAddressSerializer(many=True)
    PartyPrefix = PartyPrefixsSerializer(many=True)
    PartySubParty = MC_PartySubPartySerializer(many=True)
    Cluster = serializers.IntegerField(write_only=True,  required=False)  
    SubCluster = serializers.IntegerField(write_only=True,  required=False)
    

    class Meta:
        model =  M_Parties
        fields = '__all__'


    def create(self, validated_data):
        PartyType = validated_data.get('PartyType')
        PartyAddress_data = validated_data.pop('PartyAddress', [])
        PartyPrefix_data = validated_data.pop('PartyPrefix', [])
        PartySubPartys = validated_data.pop('PartySubParty', [])
        Cluster_id = validated_data.pop('Cluster', None)
        Sub_Cluster_id = validated_data.pop('SubCluster', None)

        PartyID = M_Parties.objects.create(**validated_data)

        for PartyAddress in PartyAddress_data:
            MC_PartyAddress.objects.create(Party=PartyID, **PartyAddress)

        for PartyPrefix in PartyPrefix_data:
            MC_PartyPrefixs.objects.create(Party=PartyID, **PartyPrefix)

        query=M_PartyType.objects.filter(id=PartyType.id).values('IsVendor', 'IsRetailer')

        if query[0]['IsVendor'] == True:
            for PartySubParty in PartySubPartys:
                subparty = PartySubParty.pop('Party')
                PartySubParty=MC_PartySubParty.objects.create(Party=PartyID,SubParty=subparty, **PartySubParty)

        else:
            
            for PartySubParty in PartySubPartys:
                PartySubParty=MC_PartySubParty.objects.create(SubParty=PartyID, **PartySubParty)

        if not query[0]['IsRetailer']:
                if Cluster_id is not None and Sub_Cluster_id is not None:
                    try:
                        cluster_instance = M_Cluster.objects.get(id=Cluster_id)
                        sub_cluster_instance = M_SubCluster.objects.get(id=Sub_Cluster_id)
                        M_PartyDetails.objects.create(Party=PartyID, Cluster=cluster_instance, SubCluster=sub_cluster_instance)
                    except M_Cluster.DoesNotExist:
                        pass
                    except M_SubCluster.DoesNotExist:
                        pass

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
        fields = ['id','Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault'] 
        
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
    
class RoutesSerializer1(serializers.ModelSerializer):
    class Meta:
        model = M_Routes
        fields = ['id', 'Name']

class PartySubPartySerializer3(serializers.ModelSerializer):
    
    Route = RoutesSerializer1()
    class Meta:
        model = MC_PartySubParty
        fields = ['Party','SubParty','Creditlimit','Route','Distance']

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Cluster
        fields = ['id','Name']

class SubClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_SubCluster
        fields = ['id','Name']

class ClusterSubClusterSerializer(serializers.ModelSerializer):
    Cluster = ClusterSerializer(read_only=True)
    SubCluster = SubClusterSerializer(read_only=True)
    class Meta:
        model = M_PartyDetails
        fields = ['Cluster','SubCluster']

class M_PartiesSerializerSecond(serializers.ModelSerializer):
    PartyAddress = PartyAddressSerializerSecond(many=True)
    City=CitiesSerializerSecond()
    District= DistrictSerializerSecond()
    State= StateSerializerSecond()
    Company = CompanySerializerSecond()
    Cluster= ClusterSubClusterSerializer(read_only=True)
    SubCluster= ClusterSubClusterSerializer(read_only=True)
    PartyType = PartyTypeSerializerSecond()
    PriceList= PriceListSerializerSecond()
    Country = CountrySerializer(read_only=True)
    PartyPrefix = PartyPrefixsSerializer(many=True)
    MCSubParty = PartySubPartySerializer3(many=True)
    
    
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

        Party_Details = M_PartyDetails.objects.filter(Party=instance.id)
        
        for aa in Party_Details:
            cluster = aa.Cluster
            subcluster = aa.SubCluster
            
            if cluster:
                ret['Cluster'] = ClusterSerializer(cluster).data
            else:
                ret['Cluster'] = None
            
            if subcluster:
                ret['SubCluster'] = SubClusterSerializer(subcluster).data
            else:
                ret['SubCluster'] = None
        
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
    ClusterName = serializers.CharField(max_length=500)
    SubClusterName = serializers.CharField(max_length=500)
    
    
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
        fields = ['Orderprefix', 'Invoiceprefix', 'Grnprefix', 'Receiptprefix','Challanprefix','WorkOrderprefix','MaterialIssueprefix','Demandprefix','IBChallanprefix','IBInwardprefix','Creditprefix','Debitprefix','PurchaseReturnprefix']
        
class UpdatePartyAddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = MC_PartyAddress
        fields = ['id','Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument']  
        
class UpdateMC_PartySubPartySerializer(serializers.ModelSerializer):
    Delete = serializers.IntegerField()
    
    class Meta:
        model =MC_PartySubParty
        fields =['Party','Route','CreatedBy','UpdatedBy','Delete']


class UpdateM_PartiesSerializer(serializers.ModelSerializer):
    PartyAddress = UpdatePartyAddressSerializer(many=True)
    PartyPrefix = UpdatePartyPrefixsSerializer(many=True)
    PartySubParty = UpdateMC_PartySubPartySerializer(many=True)
    # Cluster = serializers.IntegerField(write_only=True)
    # SubCluster = serializers.IntegerField(write_only=True)
    # Country = CountrySerializer(many=True)

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
        instance.IsApprovedParty = validated_data.get(
            'IsApprovedParty', instance.IsApprovedParty) 
        instance.Country = validated_data.get(
            'Country', instance.Country)
        
        instance.save()   

        Cluster = validated_data.get('Cluster')
        SubCluster = validated_data.get('SubCluster')
           
        
        
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
               
            
        query=M_PartyType.objects.filter(id=instance.PartyType.id).values('IsVendor','IsRetailer')
        
        if not query[0]['IsRetailer'] == True:
            if Cluster is not None and SubCluster is not None:
                M_PartyDetails.objects.filter(Party=instance, Group_id__isnull=True).update_or_create(
                Party=instance,
                defaults={'Cluster_id': Cluster, 'SubCluster_id': SubCluster},)
        
        
        if query[0]['IsVendor'] == True:
            
            for PartySubParty_data in validated_data['PartySubParty']:
                Sub_Party = PartySubParty_data.pop('Party', None)
                DeleteData = PartySubParty_data.pop('Delete', None)
                
                query = MC_PartySubParty.objects.filter(Party=instance, SubParty=Sub_Party).delete()
                if DeleteData == 0:
                    PartySubParty=MC_PartySubParty.objects.create(Party=instance, SubParty=Sub_Party, **PartySubParty_data)  
        else: 
           
            for PartySubParty_data in validated_data['PartySubParty']:
                Main_Party = PartySubParty_data.pop('Party', None)
                DeleteFlag = PartySubParty_data.pop('Delete', None)
                
                query = MC_PartySubParty.objects.filter(Party=Main_Party, SubParty=instance).delete()
                if DeleteFlag == 0:
                   PartySubParty = MC_PartySubParty.objects.create(SubParty=instance, Party=Main_Party, **PartySubParty_data)
        
        

        
        return instance
    
