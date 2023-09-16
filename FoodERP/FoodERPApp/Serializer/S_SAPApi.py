from ..models import *
from rest_framework import serializers
from ..Serializer.S_Items import *
from ..Serializer.S_Orders import  *
from ..Serializer.S_Drivers import  *
from ..Serializer.S_Vehicles import  *


class InvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_InvoiceItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch','MRPValue','GSTPercentage','QtyInNo','QtyInKg','QtyInBox']   


class InvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = InvoiceItemsSerializer(many=True)
    # InvoicesReferences = InvoicesReferencesSerializer(many=True) 
    # obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model = T_Invoices
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party','TCSAmount', 'InvoiceItems']

    def create(self, validated_data):
        # print('dddddddddddddddddddddddd',validated_data)
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
    
    
    
class InvoiceToSCMSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    InvoiceDate = serializers.DateField()
    OrderNumber = serializers.CharField(max_length=500)
    CustomerID = serializers.CharField(max_length=500)
    DriverName=serializers.CharField(max_length=100)
    VehicleNo =serializers.CharField(max_length=100)
    GSTIN =serializers.CharField(max_length=100)
    Plant=serializers.CharField(max_length=100)
    GrossAmount =serializers.DecimalField(max_digits=20, decimal_places=2)
    refInvoiceNo =serializers.CharField(max_length=100)
    refInvoiceType =serializers.CharField(max_length=100)
    refInvoiceDate =serializers.CharField(max_length=100)
    LineItemsQuantity=serializers.CharField(max_length=100)
    MaterialCode=serializers.CharField(max_length=100)
    BatchCode = serializers.CharField(max_length=500)
    BatchDate = serializers.DateField()
    QtyInNo = serializers.DecimalField(max_digits=10, decimal_places=2)
    BaseUOM = serializers.CharField(max_length=500)
    LandedPerUnitRate=serializers.DecimalField(max_digits=10, decimal_places=2)
    MRP=serializers.DecimalField(max_digits=10, decimal_places=2)
    TaxableAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST = serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST= serializers.DecimalField(max_digits=10, decimal_places=2)
    UGST= serializers.CharField(max_length=500)
    CGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    UGSTPercentage=serializers.CharField(max_length=500)
    DiscountPercentage = serializers.DecimalField(max_digits=20, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    TotalValue = serializers.DecimalField(max_digits=10, decimal_places=2)     