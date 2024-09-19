from ..models import *
from rest_framework import serializers
from FoodERPApp.models import *

class SPOSstockSerializer(serializers.ModelSerializer):
    GroupName = serializers.SerializerMethodField()
    SubGroupName = serializers.SerializerMethodField()

    class Meta:
        model = T_SPOSStock
        fields = ['StockDate', 'Item', 'BaseUnitQuantity', 'Quantity', 'Unit', 'MRP', 'MRPValue', 
                  'Party', 'CreatedBy', 'CreatedOn', 'IsSaleable', 'BatchCode', 'BatchCodeID', 
                  'Difference', 'IsStockAdjustment', 'GroupName', 'SubGroupName']

    def get_GroupName(self, obj):
        # Return the GroupName from the MC_ItemGroupDetails relation
        Item_Group_Detail = MC_ItemGroupDetails.objects.filter(
            Item=obj.Item, GroupType_id=5
        ).select_related('Group')
        return Item_Group_Detail.Group.Name if Item_Group_Detail else None

    def get_SubGroupName(self, obj):
        # Return the SubGroupName from the MC_ItemGroupDetails relation
        Item_SubGroup_Detail = MC_ItemGroupDetails.objects.filter(
            Item=obj.Item, GroupType_id=5
        ).select_related('SubGroup')
        return Item_SubGroup_Detail.SubGroup.Name if Item_SubGroup_Detail else None


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
    ActualStock=serializers.DecimalField(max_digits=10, decimal_places=3)
    ItemName = serializers.CharField(max_length=500)
    GroupTypeName = serializers.CharField(max_length=500)
    GroupName = serializers.CharField(max_length=500)
    SubGroupName = serializers.CharField(max_length=500)
    StockAdjustment=serializers.DecimalField(max_digits=10, decimal_places=3)
    