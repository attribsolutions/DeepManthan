from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers
from .S_Items import *
from .S_GRNs import *

class O_BatchWiseLiveStockSerializerForChallan(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','BaseUnitQuantity','LiveBatche','GRN']
    
class TC_GRNItemsSerializerSecondAAAAAAAAAAAAAA(serializers.ModelSerializer):
    
    Item=ItemSerializer(read_only=True)
    Unit=UnitSerializerSecond(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
   
    class Meta:
        model = TC_GRNItems
        fields = ['Item', 'Quantity', 'Unit', 'BaseUnitQuantity', 'MRP', 'ReferenceRate', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount',
                  'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode','SystemBatchCode','SystemBatchDate']  

class T_GRNSerializerForGETSecond(serializers.ModelSerializer):
    Customer = Partiesserializer(read_only=True)
    Party = Partiesserializer(read_only=True)
    GRNReferences = TC_GRNReferencesSerializer(many=True,read_only=True)
    GRNItems = TC_GRNItemsSerializerSecondAAAAAAAAAAAAAA(many=True)
    BatchWiseLiveStockGRNID = O_BatchWiseLiveStockSerializerForChallan(read_only=True,many=True)
    class Meta:
        model = T_GRNs
        fields = ['id', 'GRNDate', 'Customer', 'GRNNumber', 'FullGRNNumber','InvoiceNumber','GrandTotal', 'Party', 'CreatedBy', 'UpdatedBy','CreatedOn', 'GRNReferences', 'GRNItems','BatchWiseLiveStockGRNID']

class ChallanItemsSerializer(serializers.ModelSerializer):  
    class Meta:
        model = TC_ChallanItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate']  

class ChallanSerializer(serializers.ModelSerializer):
    ChallanItems = ChallanItemsSerializer(many=True)
    BatchWiseLiveStockGRNID=O_BatchWiseLiveStockSerializerForChallan(many=True)
    class Meta:
        model = T_Challan
        fields = ['ChallanDate', 'ChallanNumber', 'FullChallanNumber', 'GrandTotal', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'ChallanItems', 'GRN','BatchWiseLiveStockGRNID']    
    
    def create(self, validated_data):
        ChallanItems_data = validated_data.pop('ChallanItems')
        O_BatchWiseLiveStockItems_data = validated_data.pop('BatchWiseLiveStockGRNID')
        ChallanID = T_Challan.objects.create(**validated_data)
        
        for ChallanItem_data in ChallanItems_data:
            ChallanItemID =TC_ChallanItems.objects.create(Challan=ChallanID, **ChallanItem_data)
            
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
            OBatchQuantity=O_BatchWiseLiveStock.objects.filter(LiveBatche=O_BatchWiseLiveStockItem_data['LiveBatche']).values('BaseUnitQuantity')
                
            if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(LiveBatche=O_BatchWiseLiveStockItem_data['LiveBatche']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                UpdateChildetable=TC_ChallanItems.objects.filter(Challan=ChallanID,Item=O_BatchWiseLiveStockItem_data['Item']).update(LiveBatch=O_BatchWiseLiveStockItem_data['LiveBatche'])
            else:
                raise serializers.ValidationError("Not In Stock ")
                    
        return ChallanID   
             