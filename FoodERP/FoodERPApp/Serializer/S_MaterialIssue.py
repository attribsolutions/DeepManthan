from dataclasses import fields
from rest_framework import serializers
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_Companies import *
from ..Serializer.S_Parties import *


  
class StockQtyserializerForMaterialIssue(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','BatchDate','BatchCode','SystemBatchDate','SystemBatchCode','Quantity','BaseUnitQuantity','Party']  

class MaterialIssueItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_MaterialIssueItems
        fields =['id', 'WorkOrderQuantity', 'IssueQuantity', 'BatchDate', 'BatchCode', 'BatchCodeQuantity', 'SystemBatchDate', 'SystemBatchCode', 'Item', 'MaterialIssue', 'Unit']

class MaterialIssueSerializer(serializers.ModelSerializer):
    MaterialIssueItems = MaterialIssueItemsSerializer(many=True)
    class Meta:
        model = T_MaterialIssue
        fields = ['id', 'MaterialIssueDate', 'NumberOfLot', 'LotQuantity', 'Status', 'ReIssueID', 'IsReIssueID', 'CreatedBy','UpdatedBy','Company','Party','Item','MaterialIssueItems']

# Get ALL ,Get Single BOM

class MaterialIssueItemsSerializerSecond(serializers.ModelSerializer):
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    class Meta:
        model =  TC_MaterialIssueItems
        fields = ['id', 'WorkOrderQuantity', 'IssueQuantity', 'BatchDate', 'BatchCode','BatchCodeQuantity', 'SystemBatchDate', 'SystemBatchCode', 'Item', 'MaterialIssue', 'Unit']     
        
class MatetrialIssueSerializerSecond(serializers.ModelSerializer):
    MaterialIssueItems = MaterialIssueItemsSerializerSecond(many=True)
    Item = M_ItemsSerializer01(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    Party = DivisionsSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model = T_MaterialIssue
        fields = ['MaterialIssueDate','Item','Unit','Bom','NumberOfLot','Quantity','Company','Party','CreatedBy','UpdatedBy','MaterialIssueItems']
    
           