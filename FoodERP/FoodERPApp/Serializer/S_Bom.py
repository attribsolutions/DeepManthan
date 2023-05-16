from rest_framework import serializers
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_Companies import *
# Post and Put Methods Serializer

class MC_BOMItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MC_BillOfMaterialItems
        fields = ['Quantity','Item','Unit'] 

class M_BOMSerializer(serializers.ModelSerializer):
    BOMItems = MC_BOMItemsSerializer(many=True)
    class Meta:
        model = M_BillOfMaterial
        fields = ['BomDate','EstimatedOutputQty','Comment','IsActive','IsVDCItem','Item','Unit','Company','CreatedBy','ReferenceBom','BOMItems']  
        
    def create(self, validated_data):
        BomItems_data = validated_data.pop('BOMItems')
        BomID= M_BillOfMaterial.objects.create(**validated_data)
        
        for BomItem_data in BomItems_data:
            BomItem = MC_BillOfMaterialItems.objects.create(BOM=BomID, **BomItem_data)
            
        return BomID  

    def update(self, instance, validated_data):

        instance.BomDate = validated_data.get(
            'BomDate', instance.BomDate)
        instance.EstimatedOutputQty = validated_data.get(
            'EstimatedOutputQty', instance.EstimatedOutputQty)
        instance.Comment = validated_data.get(
            'Comment', instance.Comment)
        instance.IsActive = validated_data.get(
            'IsActive', instance.IsActive)
        
        instance.IsVDCItem = validated_data.get(
            'IsVDCItem', instance.IsVDCItem)
        
        instance.Item = validated_data.get(
            'Item', instance.Item)
        instance.Unit = validated_data.get(
            'Unit', instance.Unit)
        instance.Company = validated_data.get(
            'Company', instance.Company)
          
        instance.save()

        for a in instance.BOMItems.all():
            a.delete()

        for BomItem_data in  validated_data['BOMItems']:
            MaterialItems = MC_BillOfMaterialItems.objects.create(BOM=instance, **BomItem_data)

        return instance        
        
       

# Get ALL Category,Get Single BOM

class MC_BOMItemsSerializerSecond(serializers.ModelSerializer):
    Item = M_ItemsSerializer01(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model =  MC_BillOfMaterialItems
        fields = ['id','Quantity','Item','Unit'] 

class  M_BOMSerializerSecond(serializers.ModelSerializer):
    BOMItems = MC_BOMItemsSerializerSecond(many=True,read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    class Meta:
        model = M_BillOfMaterial
        fields = ['id','BomDate','EstimatedOutputQty','Comment','IsActive','IsVDCItem','Item','Unit','Company','CreatedOn','BOMItems'] 
        
class StockQtyserializer(serializers.Serializer):
    id = serializers.IntegerField()
    actualStock = serializers.DecimalField(max_digits=10, decimal_places=3)
    Item_id=serializers.IntegerField()        
             