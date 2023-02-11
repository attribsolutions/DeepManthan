from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers
from ..Serializer.S_Items import *
from ..Serializer.S_Orders import  *


class VDCChallanItemsSerializer(serializers.ModelSerializer):  
    class Meta:
        model = TC_VDCChallanItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch']  

class VDCChallanSerializer(serializers.ModelSerializer):
    VDCChallanItems = VDCChallanItemsSerializer(many=True)
    class Meta:
        model = T_VDCChallan
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'VDCChallanItems', 'GRN']         