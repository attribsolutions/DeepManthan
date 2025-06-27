from ..models import *
from rest_framework import serializers
from ..Serializer.S_Routes import  *
from django.utils import timezone
import os

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

        
class PartyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = ['Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument','fssaidocumenturl']  
    
class PartyPrefixsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyPrefixs
        fields = ['Orderprefix', 'Invoiceprefix', 'Grnprefix', 'Receiptprefix','Challanprefix','WorkOrderprefix','MaterialIssueprefix','Demandprefix','IBChallanprefix','IBInwardprefix','PurchaseReturnprefix','Creditprefix','Debitprefix']

        
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
    PartyAddress = PartyAddressSerializer(many=True )
    PartyPrefix = PartyPrefixsSerializer(many=True)
    PartySubParty = MC_PartySubPartySerializer(many=True)
    Cluster = serializers.IntegerField(write_only=True,  required=False)  
    SubCluster = serializers.IntegerField(write_only=True,  required=False)

    class Meta:
        model = M_Parties
        fields = [
            'id', 'Name', 'ShortName', 'PriceList', 'PartyType', 'Company', 'PAN', 'Email',
            'MobileNo', 'AlternateContactNo', 'Country', 'State', 'District', 'City', 'SAPPartyCode',
             'Latitude', 'Longitude', 'GSTIN', 'isActive', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn',
            'IsApprovedParty', 'IsDivision', 'MkUpMkDn', 'SkyggeID', 'UploadSalesDatafromExcelParty',
            'ClosingDate', 'PartyAddress', 'PartyPrefix', 'PartySubParty', 'Cluster', 'SubCluster'
        ]
        
        
    def create(self, validated_data):
        PartyType = validated_data.get('PartyType')
        PartyAddress_data = validated_data.pop('PartyAddress', [])
        PartyPrefix_data = validated_data.pop('PartyPrefix', [])
        PartySubPartys = validated_data.pop('PartySubParty', [])
        Cluster_id = validated_data.pop('Cluster', None)
        Sub_Cluster_id = validated_data.pop('SubCluster', None)

        PartyID = M_Parties.objects.create(**validated_data)

        # ✅ Use the nested serializer to save addresses
        for address_data in PartyAddress_data:
            address_data.pop('RowID', None)  # Remove RowID
            address_serializer = PartyAddressSerializer(data=address_data)
            if address_serializer.is_valid(raise_exception=True):
                address_serializer.save(Party=PartyID)


        # ✅ Save other related nested data as before
        for PartyPrefix in PartyPrefix_data:
            MC_PartyPrefixs.objects.create(Party=PartyID, **PartyPrefix)

        query = M_PartyType.objects.filter(id=PartyType.id).values('IsVendor', 'IsRetailer')

        if query[0]['IsVendor']:
            for PartySubParty in PartySubPartys:
                subparty = PartySubParty.pop('Party')
                MC_PartySubParty.objects.create(Party=PartyID, SubParty=subparty, **PartySubParty)
        else:
            for PartySubParty in PartySubPartys:
                MC_PartySubParty.objects.create(SubParty=PartyID, **PartySubParty)

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
    fssaidocumenturl = serializers.SerializerMethodField()

    class Meta:
        model = MC_PartyAddress
        fields = ['id', 'Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument', 'fssaidocumenturl']

    def get_fssaidocumenturl(self, obj):
        if obj.fssaidocumenturl:
            url_prefix = NewURLPrefix()
            file_name = os.path.basename(obj.fssaidocumenturl.name) 
            table_code = 4 
            media_url = f"{url_prefix}/{file_name}/{obj.id}/{table_code}"
            return media_url
        return None


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
        fields = ['id','Address', 'FSSAINo', 'FSSAIExipry', 'PIN', 'IsDefault', 'fssaidocument', 'fssaidocumenturl']  
        
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
        # Update M_Parties main fields
        for attr, value in validated_data.items():
            if attr not in ['PartyPrefix', 'PartyAddress', 'PartySubParty', 'Cluster', 'SubCluster']:
                setattr(instance, attr, value)

        ExistingStatus_isActive = instance.isActive
        Updated_isActive = validated_data.get('isActive', ExistingStatus_isActive)

        if ExistingStatus_isActive != Updated_isActive:
            instance.isActive = Updated_isActive
            instance.ClosingDate = timezone.now() if not Updated_isActive else None

        instance.save()

        # 1️⃣ PartyPrefix — delete old, insert new
        instance.PartyPrefix.all().delete()
        for prefix_data in validated_data.get('PartyPrefix', []):
            MC_PartyPrefixs.objects.create(Party=instance, **prefix_data)

        # 2️⃣ PartyAddress — update existing, create new if id not provided
        for address_data in validated_data.get('PartyAddress', []):
            address_id = int(address_data.get('id', 0))
            fssai_doc = address_data.get('fssaidocumenturl', None)

            if address_id > 0:
                # Update existing
                update_fields = {
                    'Address': address_data['Address'],
                    'FSSAINo': address_data['FSSAINo'],
                    'FSSAIExipry': address_data['FSSAIExipry'],
                    'PIN': address_data['PIN'],
                    'IsDefault': address_data['IsDefault']
                }
                if fssai_doc:
                    update_fields['fssaidocumenturl'] = fssai_doc

                MC_PartyAddress.objects.filter(id=address_id, Party=instance).update(**update_fields)

            else:
                # Create new
                address_data.pop('id', None)
                MC_PartyAddress.objects.create(Party=instance, **address_data)

        # 3️⃣ Update M_PartyDetails Cluster/SubCluster
        query = M_PartyType.objects.filter(id=instance.PartyType.id).values('IsVendor', 'IsRetailer').first()
        if not query['IsRetailer']:
            Cluster = validated_data.get('Cluster')
            SubCluster = validated_data.get('SubCluster')
            if Cluster is not None and SubCluster is not None:
                M_PartyDetails.objects.update_or_create(
                    Party=instance,
                    Group_id__isnull=True,
                    defaults={'Cluster_id': Cluster, 'SubCluster_id': SubCluster}
                )

        # 4️⃣ PartySubParty — delete & create as per Delete flag
        if query['IsVendor']:
            for subparty_data in validated_data.get('PartySubParty', []):
                sub_party = subparty_data.pop('Party', None)
                delete_flag = subparty_data.pop('Delete', None)

                MC_PartySubParty.objects.filter(Party=instance, SubParty=sub_party).delete()
                if delete_flag == 0:
                    MC_PartySubParty.objects.create(Party=instance, SubParty=sub_party, **subparty_data)
        else:
            for subparty_data in validated_data.get('PartySubParty', []):
                main_party = subparty_data.pop('Party', None)
                delete_flag = subparty_data.pop('Delete', None)

                MC_PartySubParty.objects.filter(Party=main_party, SubParty=instance).delete()
                if delete_flag == 0:
                    MC_PartySubParty.objects.create(SubParty=instance, Party=main_party, **subparty_data)

        return instance