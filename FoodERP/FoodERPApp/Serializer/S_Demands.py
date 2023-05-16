from ..models import *
from rest_framework import serializers
from .S_Orders import * 
from .S_Parties import * 
from .S_Items import * 
from .S_GSTHSNCode import * 
from .S_Margins import * 
from .S_Mrps import * 
from .S_TermsAndConditions import *

# POST Method
class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name']  
        
class TC_DemandItemsSerializer(serializers.ModelSerializer):
   class Meta:
        model = TC_DemandItems
        fields = ['Item','Quantity','MRP','Rate','Unit','BaseUnitQuantity','GST','Margin','BasicAmount','GSTAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','Amount', 'IsDeleted']

class T_DemandSerializer(serializers.ModelSerializer):
    DemandItem = TC_DemandItemsSerializer(many=True)
    class Meta:
        model = T_Demands
        fields = ['id','DemandDate','Customer','Supplier','DemandNo','FullDemandNumber', 'Division','DemandAmount','Comment','BillingAddress','ShippingAddress', 'MaterialIssue','CreatedBy', 'UpdatedBy', 'DemandItem']

    def create(self, validated_data):
        DemandItems_data = validated_data.pop('DemandItem')
        Demand = T_Demands.objects.create(**validated_data)
        
        for DemandItem_data in DemandItems_data:
            Items=TC_DemandItems.objects.create(Demand=Demand, **DemandItem_data)
            
        return Demand
    
    def update(self, instance, validated_data):
        
        instance.DemandDate = validated_data.get(
            'DemandDate', instance.DemandDate)      
        instance.DemandAmount = validated_data.get(
            'DemandAmount', instance.DemandAmount)
        instance.Comment = validated_data.get(
            'Comment', instance.Comment)
        instance.BillingAddress = validated_data.get(
            'BillingAddress', instance.BillingAddress)
        instance.ShippingAddress = validated_data.get(
            'ShippingAddress', instance.ShippingAddress)
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy) 
                
        instance.save()


        for DemandItem_data in validated_data['DemandItem']:
            if(DemandItem_data['Quantity'] == 0 and DemandItem_data['IsDeleted'] == 1 ) :
                SetFlag=TC_DemandItems.objects.filter(Item=DemandItem_data['Item'],Demand=instance,IsDeleted=0).update(IsDeleted=1)
            elif(DemandItem_data['IsDeleted'] == 0 ) :
                SetFlag=TC_DemandItems.objects.filter(Item=DemandItem_data['Item'],Demand=instance,IsDeleted=0)
                
                if SetFlag.count() == 0:
                    DemandItem_data['IsDeleted']=0
                    Items = TC_DemandItems.objects.create(Demand=instance, **DemandItem_data)
            else: 
                SetFlag=TC_DemandItems.objects.filter(Item=DemandItem_data['Item'],Demand=instance).update(IsDeleted=1)
                DemandItem_data['IsDeleted']=0
                Items = TC_DemandItems.objects.create(Demand=instance, **DemandItem_data)
        return instance

class T_DemandSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Supplier = PartiesSerializerSecond(read_only=True)
    BillingAddress = PartyAddressSerializerSecond(read_only=True) 
    ShippingAddress = PartyAddressSerializerSecond(read_only=True) 
    class Meta:
        model = T_Demands
        fields = '__all__'
    

class UnitSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class Mc_ItemUnitSerializerThird(serializers.ModelSerializer):
    UnitID = UnitSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID','BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion'] 
        
        
class TC_DemandItemsSerializerSecond(serializers.ModelSerializer):
    
    MRP = M_MRPsSerializer(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    Margin = M_MarginsSerializer(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta:
        model = TC_DemandItems
        fields = '__all__'
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(TC_DemandItemsSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("MRP", None):
            ret["MRP"] = {"id": None, "MRP": None}
            
        if not ret.get("Margin", None):
            ret["Margin"] = {"id": None, "Margin": None}    
        return ret 


class TC_DemandSerializerThird(serializers.ModelSerializer):
    Customer = PartiesSerializerThird(read_only=True)
    Supplier = PartiesSerializerThird(read_only=True)
    DemandItem = TC_DemandItemsSerializerSecond(read_only=True,many=True)
    BillingAddress=PartyAddressSerializerSecond(read_only=True) 
    ShippingAddress=PartyAddressSerializerSecond(read_only=True) 

    class Meta:
        model = T_Demands
        fields = '__all__'         


class DemandSerializerForInterBranchInward(serializers.Serializer):
    id=serializers.IntegerField()
    SupplierName = serializers.CharField(max_length=500)     
    DemandAmount=serializers.DecimalField(max_digits=10, decimal_places=2) 
    CustomerID =serializers.IntegerField()

                
class DemandEditserializer(serializers.Serializer):
    # id=serializers.IntegerField()
    Item_id=serializers.IntegerField()
    ItemName=serializers.CharField(max_length=100)
    Quantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    MRP_id=serializers.IntegerField() 
    MRPValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)
    Unit_id=serializers.IntegerField() 
    UnitName=serializers.CharField(max_length=100)
    BaseUnitQuantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    GST_id=serializers.IntegerField() 
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    HSNCode=serializers.CharField(max_length=100)
    Margin_id=serializers.IntegerField() 
    MarginValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    BasicAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount=serializers.DecimalField(max_digits=10, decimal_places=2)  
              