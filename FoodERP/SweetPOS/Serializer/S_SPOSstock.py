from ..models import *
from rest_framework import serializers
from FoodERPApp.models import *


class SPOSstockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = T_SPOSStock
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = ['id', 'Name']

class SPOSStockReportSerializer(serializers.Serializer):
    
    
    Item_id=serializers.IntegerField()
    Unit=serializers.IntegerField()
    UnitName=serializers.CharField(max_length=500)
    OpeningBalance=serializers.DecimalField(max_digits=10, decimal_places=3)
    GRNInward=serializers.DecimalField(max_digits=10, decimal_places=3)
    SalesReturn = serializers.DecimalField(max_digits=10, decimal_places=3)
    Sale = serializers.DecimalField(max_digits=10, decimal_places=3)
    PurchaseReturn = serializers.DecimalField(max_digits=10, decimal_places=3)
    ClosingBalance=serializers.DecimalField(max_digits=10, decimal_places=3)
    ClosingAmount = serializers.DecimalField(max_digits=10, decimal_places=3)
    ActualStock=serializers.DecimalField(max_digits=10, decimal_places=3)
    ItemName = serializers.CharField(max_length=500)
    GroupTypeName = serializers.CharField(max_length=500)
    GroupName = serializers.CharField(max_length=500)
    SubGroupName = serializers.CharField(max_length=500)
    StockAdjustment=serializers.DecimalField(max_digits=10, decimal_places=3)
    