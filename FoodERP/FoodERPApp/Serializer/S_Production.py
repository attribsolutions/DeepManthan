
from ..Serializer.S_GRNs import O_BatchWiseLiveStockSerializer
from ..models import *
from rest_framework import serializers
from ..Serializer.S_Companies import *
from ..Serializer.S_Parties import *
from ..Serializer.S_Items import *

class ProductionMaterialIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model =TC_ProductionMaterialIssue
        fields=['MaterialIssue']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=M_Items
        fields=['id','Name']

class H_ProductionSerializerforGET(serializers.ModelSerializer):
    ProductionMaterialIssue=ProductionMaterialIssueSerializer(many=True)
    Item=ItemSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    Division = DivisionsSerializer(read_only=True)
    
    class Meta:
        model = T_Production
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super(H_ProductionSerializerforGET, self).to_representation(instance)
        data['Company'] = instance.Company.id
        data['CompanyName'] = instance.Company.Name
        data['Division'] = instance.Division.id
        data['DivisionName'] = instance.Division.Name
        data['Unit'] = instance.Unit.id
        data['UnitName'] = instance.Unit.UnitID.Name
        data['Item'] = instance.Item.id
        data['ItemName'] = instance.Item.Name
       
        return data    
        

class O_BatchWiseLiveStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['Item','Quantity','Unit','OriginalBaseUnitQuantity','BaseUnitQuantity','Party','CreatedBy']
    
class O_LiveBatchesSerializer(serializers.ModelSerializer):
    
    O_BatchWiseLiveStockList = O_BatchWiseLiveStockSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','GST','Rate','BatchDate', 'BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList']
    

class H_ProductionSerializer(serializers.ModelSerializer):
    ProductionMaterialIssue=ProductionMaterialIssueSerializer(many=True)
    O_LiveBatchesList=O_LiveBatchesSerializer(many=True)
    class Meta:
        model = T_Production
        fields = '__all__'

    def create(self, validated_data):
        ProductionMaterialIssues_data = validated_data.pop('ProductionMaterialIssue')
        O_LiveBatchesLists_data=validated_data.pop('O_LiveBatchesList')
        
        ProductionID= T_Production.objects.create(**validated_data)
       
        for O_LiveBatchesList_data in O_LiveBatchesLists_data :
            O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
            BatchID=O_LiveBatches.objects.create(**O_LiveBatchesList_data)
            for O_BatchWiseLiveStockList in O_BatchWiseLiveStockLists:
                O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(Production=ProductionID,LiveBatche=BatchID,**O_BatchWiseLiveStockList)  
            
        for ProductionMaterialIssue_data in ProductionMaterialIssues_data:
            Productionreff = TC_ProductionMaterialIssue.objects.create(Production=ProductionID, **ProductionMaterialIssue_data)
            
        return ProductionID



class ProductionMaterialIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model =TC_ProductionMaterialIssue
        fields='__all__'

class M_MaterialissueItemsserializer(serializers.ModelSerializer):
    class Meta:
        model=M_Items
        fields=['id','Name']

class H_ProductionSerializer2(serializers.ModelSerializer):
    Item=M_MaterialissueItemsserializer(read_only=True)
    class Meta:
        model = T_MaterialIssue
        fields = '__all__'

class UnitSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class ItemUnitsSerializerSecond(serializers.ModelSerializer):
    UnitID = UnitSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID', 'BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit']

class MaterialIssueSerializer(serializers.ModelSerializer):
    Item=M_MaterialissueItemsserializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model = T_MaterialIssue
        fields = '__all__'
        fields = ['id','NumberOfLot','LotQuantity','Item','Unit']
    