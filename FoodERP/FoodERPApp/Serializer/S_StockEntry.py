from ..models import *
from rest_framework import serializers
from collections import OrderedDict
from ..Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from .S_GSTHSNCode import *
from .S_Orders import * 



class PartyStockEntryOBatchWiseLiveStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['Item','Quantity','Unit','OriginalBaseUnitQuantity','BaseUnitQuantity','Party','CreatedBy']


class PartyStockEntryOLiveBatchesSerializer(serializers.ModelSerializer):
    
    O_BatchWiseLiveStockList = PartyStockEntryOBatchWiseLiveStockSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','GST','BatchDate','BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','GSTPercentage','MRPValue','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList']
        
        
    def create(self, validated_data):
           
        O_BatchWiseLiveStockListItems_data = validated_data.pop('O_BatchWiseLiveStockList')
        OLiveBatcheID = O_LiveBatches.objects.create(**validated_data)
        
        for O_BatchWiseLiveStockItems_data in O_BatchWiseLiveStockListItems_data:
            GrnItem=O_BatchWiseLiveStock.objects.create(LiveBatche=OLiveBatcheID, **O_BatchWiseLiveStockItems_data)    
        
        return OLiveBatcheID    