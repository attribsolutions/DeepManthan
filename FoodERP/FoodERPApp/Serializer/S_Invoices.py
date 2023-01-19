from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers

class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name']

class UnitSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class Mc_ItemUnitSerializerThird(serializers.ModelSerializer):
    UnitID = UnitSerializerThird(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID','BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit'] 
class LiveBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model =O_LiveBatches
        fields='__all__'

class StockQtyserializerForInvoice(serializers.ModelSerializer):
    LiveBatche=LiveBatchSerializer()
    Unit = Mc_ItemUnitSerializerThird()
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','BaseUnitQuantity','Party','LiveBatche','Unit']  

class OrderserializerforInvoice(serializers.ModelSerializer):
    class Meta:
        model = T_Orders
        fields = '__all__'



class InvoicesReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InvoicesReferences
        fields = ['Order']
        
class InvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_InvoiceItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GSTPercentage', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate']   

class obatchwiseStockSerializer(serializers.ModelSerializer):
    class Meta:
        model=O_BatchWiseLiveStock
        fields=['Quantity','BaseUnitQuantity','Item']
        
class InvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = InvoiceItemsSerializer(many=True)
    InvoicesReferences = InvoicesReferencesSerializer(many=True) 
    obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model = T_Invoices
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'CustomerGSTTin', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'InvoiceItems', 'InvoicesReferences', 'obatchwiseStock']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        InvoicesReferences_data = validated_data.pop('InvoicesReferences')
        O_BatchWiseLiveStockItems_data = validated_data.pop('obatchwiseStock')
        InvoiceID = T_Invoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemID =TC_InvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                    
                    raise serializers.ValidationError("Not In Stock ")    
          
        for InvoicesReference_data in InvoicesReferences_data:
            InvoicesReferences = TC_InvoicesReferences.objects.create(Invoice=InvoiceID, **InvoicesReference_data)       
        
        return InvoiceID   
    
    
    
class InvoiceSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
 
    class Meta:
        model = T_Invoices
        fields = '__all__'        