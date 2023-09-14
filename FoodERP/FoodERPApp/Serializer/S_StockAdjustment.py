from rest_framework import serializers
from ..models import *

    
class OBatchWiseLiveStockAdjustmentSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    Item_id= serializers.IntegerField()
    ItemName = serializers.CharField(max_length=100) 
    OriginalBaseUnitQuantity = serializers.DecimalField(max_digits=20, decimal_places=3)
    BaseUnitQuantity = serializers.DecimalField(max_digits=20, decimal_places=3)
    BatchDate = serializers.CharField(max_length=100) 
    BatchCode = serializers.CharField(max_length=100) 
    SystemBatchDate = serializers.CharField(max_length=100) 
    SystemBatchCode = serializers.CharField(max_length=100) 
    MRPValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    MRPID = serializers.IntegerField()
    MRP = serializers.DecimalField(max_digits=10, decimal_places=2)
    GST_id=serializers.IntegerField()
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    UnitID = serializers.IntegerField()
    UnitName = serializers.CharField(max_length=100) 
    
    
    