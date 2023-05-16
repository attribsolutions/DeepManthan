from ..models import *
from rest_framework import serializers
from ..Serializer.S_Items import *
from ..Serializer.S_Orders import  *
from ..Serializer.S_Drivers import  *
from ..Serializer.S_Vehicles import  *


class InvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_InvoiceItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch','MRPValue','GSTPercentage']   


class InvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = InvoiceItemsSerializer(many=True)
    # InvoicesReferences = InvoicesReferencesSerializer(many=True) 
    # obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model = T_Invoices
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'InvoiceItems']

    def create(self, validated_data):
        print('dddddddddddddddddddddddd',validated_data)
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        # InvoicesReferences_data = validated_data.pop('InvoicesReferences')
        # O_BatchWiseLiveStockItems_data = validated_data.pop('obatchwiseStock')
        InvoiceID = T_Invoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemID =TC_InvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        # for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
        #         OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
        #         print(OBatchQuantity[0]['BaseUnitQuantity'],O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
        #         if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
        #             OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
        #         else:
                    
        #             raise serializers.ValidationError("Not In Stock ")    
          
        # for InvoicesReference_data in InvoicesReferences_data:
        #     print(InvoiceID) 
        #     InvoicesReferences = TC_InvoicesReferences.objects.create(Invoice=InvoiceID, **InvoicesReference_data)   
              
        
        return InvoiceID 