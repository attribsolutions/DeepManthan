from dataclasses import field
import re
from ..models import *
from rest_framework import serializers
from collections import OrderedDict
from ..Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from .S_GSTHSNCode import * 

class Partiesserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id', 'Name']
        
''' POST AND PUT Methods Serializers  Save/Edit  Create/Update '''
class O_BatchWiseLiveStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['Item','Quantity','Unit','OriginalBaseUnitQuantity','BaseUnitQuantity','Party','CreatedBy']
    
class O_LiveBatchesSerializer(serializers.ModelSerializer):
    
    O_BatchWiseLiveStockList = O_BatchWiseLiveStockSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','GST','Rate','BatchDate', 'BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList']
    


class TC_InterBranchInwardReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_GRNReferences
        fields = ['Demand', 'IBChallan', 'IsInward']        

class TC_InterBranchInwardItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InterBranchInwardItems
        fields = ['Item', 'Quantity', 'Unit', 'BaseUnitQuantity', 'MRP', 'ReferenceRate', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount',
                  'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode','SystemBatchCode','SystemBatchDate']

class T_InterBranchInwardSerializer(serializers.ModelSerializer):

    InterBranchInwardItems = TC_InterBranchInwardItemsSerializer(many=True)
    
    O_LiveBatchesList=O_LiveBatchesSerializer(many=True)
    
    InterBranchInwardReferences = TC_InterBranchInwardReferencesSerializer(many=True) 
    class Meta:
        model = T_InterBranchInward
        fields = ['IBInwardDate', 'IBInwardNumber', 'FullIBInwardNumber', 'GrandTotal', 'CreatedBy', 'UpdatedBy', 'Customer', 'Supplier','InterBranchInwardItems','InterBranchInwardReferences', 'O_LiveBatchesList']
       
    def create(self, validated_data):
       
        IBInwardItems_data = validated_data.pop('InterBranchInwardItems')
        O_LiveBatchesLists_data=validated_data.pop('O_LiveBatchesList')
        
        IBInwardReferences_data = validated_data.pop('InterBranchInwardReferences')
        
        IBInwardID = T_InterBranchInward.objects.create(**validated_data)
        
        for IBInwardItem_data in IBInwardItems_data :
            InwardItem=TC_InterBranchInwardItems.objects.create(IBInward=IBInwardID, **IBInwardItem_data)
 
        for O_LiveBatchesList_data in O_LiveBatchesLists_data :
            O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
            BatchID=O_LiveBatches.objects.create(**O_LiveBatchesList_data)
            for O_BatchWiseLiveStockList in O_BatchWiseLiveStockLists:
                O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(IBInward=IBInwardID,LiveBatche=BatchID,**O_BatchWiseLiveStockList)  
            
        
        for IBInwardReference_data in IBInwardReferences_data:
            IBInwardReferences=TC_InterBranchInwardReferences.objects.create(IBInward=IBInwardID, **IBInwardReference_data)
            
       
        return IBInwardID
      


'''Single Record Details Fetch Get Methods Serializer '''


class Partiesserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id', 'Name']

class TC_IBInwardReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InterBranchInwardReferences
        fields = ['Demand', 'IBChallan', 'IsInward'] 
        
class ItemSerializer(serializers.ModelSerializer):
    class Meta : 
        model = M_Items
        fields = ['id','Name']

class Unitserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['Name']

class UnitSerializerSecond(serializers.ModelSerializer):
    UnitID= serializers.SlugRelatedField(read_only=True,slug_field='Name')
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID']          

class TC_InterBranchInwardItemsSerializerSecond(serializers.ModelSerializer):
    
    Item=ItemSerializer(read_only=True)
    Unit=UnitSerializerSecond(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    class Meta:
        model = TC_InterBranchInwardItems
        fields = ['Item', 'Quantity', 'Unit', 'BaseUnitQuantity', 'MRP', 'ReferenceRate', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount',
                  'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode','SystemBatchCode','SystemBatchDate']          


class T_InterBranchInwardSerializerForGET(serializers.ModelSerializer):
    Customer = Partiesserializer(read_only=True)
    Supplier = Partiesserializer(read_only=True)
    InterBranchInwardReferences = TC_IBInwardReferencesSerializer(many=True,read_only=True)
    InterBranchInwardItems = TC_InterBranchInwardItemsSerializerSecond(many=True)

    class Meta:
        model = T_InterBranchInward
        fields = ['id', 'IBInwardDate', 'IBInwardNumber', 'FullIBInwardNumber', 'GrandTotal', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'Customer', 'Supplier','InterBranchInwardItems','InterBranchInwardReferences']
