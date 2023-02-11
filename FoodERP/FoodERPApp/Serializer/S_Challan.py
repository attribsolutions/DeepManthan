from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers
from .S_Items import *
from .S_Orders import  *


class ChallanItemsSerializer(serializers.ModelSerializer):  
    class Meta:
        model = TC_ChallanItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch']  

class ChallanSerializer(serializers.ModelSerializer):
    ChallanItems = ChallanItemsSerializer(many=True)
    class Meta:
        model = T_Challan
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'ChallanItems', 'GRN']         