from ..models import *
from rest_framework import serializers
from collections import OrderedDict
from ..Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from .S_GSTHSNCode import *
from .S_Orders import * 



class PartyStockEntryT_StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = T_Stock
        fields = ['StockDate','Item','Quantity','Unit','BaseUnitQuantity','MRPValue','MRP','Party','CreatedBy','BatchCode','Difference','IsSaleable','BatchCodeID']
    
class PartyStockEntryOBatchWiseLiveStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['Item','Quantity','Unit','OriginalBaseUnitQuantity','BaseUnitQuantity','Party','CreatedBy']

class PartyStockEntryOLiveBatchesSerializer(serializers.ModelSerializer):
    
    T_StockEntryList = PartyStockEntryT_StockSerializer(many=True)
    O_BatchWiseLiveStockList = PartyStockEntryOBatchWiseLiveStockSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','GST','BatchDate','BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','GSTPercentage','MRPValue','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList','T_StockEntryList']
        
        
    def create(self, validated_data):
       
        O_BatchWiseLiveStockListItems_data = validated_data.pop('O_BatchWiseLiveStockList')
        T_StockEntryItemsList_data = validated_data.pop('T_StockEntryList')
        OLiveBatcheID = O_LiveBatches.objects.create(**validated_data)
        
        for T_StockEntryItem_data in T_StockEntryItemsList_data:
            StockItem=T_Stock.objects.create(**T_StockEntryItem_data)
        
        for O_BatchWiseLiveStockItems_data in O_BatchWiseLiveStockListItems_data:
            GrnItem=O_BatchWiseLiveStock.objects.create(LiveBatche=OLiveBatcheID, **O_BatchWiseLiveStockItems_data)    
        
        return OLiveBatcheID    

class PartyStockAdjustmentOLiveBatchesSerializer(serializers.ModelSerializer):
    
    T_StockEntryList = PartyStockEntryT_StockSerializer(many=True)
    O_BatchWiseLiveStockList = PartyStockEntryOBatchWiseLiveStockSerializer(many=True)
    Mode=serializers.IntegerField()
    class Meta:
        model = O_LiveBatches
        fields = ['Mode','MRP','GST','BatchDate','BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','GSTPercentage','MRPValue','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList','T_StockEntryList']
        
        
    def create(self, validated_data):
        O_BatchWiseLiveStockListItems_data = validated_data.pop('O_BatchWiseLiveStockList')
        T_StockEntryItemsList_data = validated_data.pop('T_StockEntryList')
        
        if validated_data['Mode'] == 2 : 
            for T_StockEntryItem_data in T_StockEntryItemsList_data:
                StockItem=T_Stock.objects.create(**T_StockEntryItem_data)
        
        for O_BatchWiseLiveStockItems_data in O_BatchWiseLiveStockListItems_data:
            GrnItem=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItems_data['BatchCodeID']).update(BaseUnitQuantity=O_BatchWiseLiveStockItems_data['BaseUnitQuantity'])    
        
        return GrnItem