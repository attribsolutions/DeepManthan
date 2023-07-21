from ..Views.V_CommFunction import *
from ..models import *
from rest_framework import serializers


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_DiscountMaster
        fields = '__all__'

class DiscountMasterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ItemID = serializers.IntegerField()
    ItemName = serializers.CharField(max_length=500)
    DiscountType = serializers.IntegerField() 
    Discount = serializers.DecimalField(max_digits=20, decimal_places=2)
    GroupTypeName = serializers.CharField(max_length=500)
    GroupName = serializers.CharField(max_length=500)
    SubGroupName = serializers.CharField(max_length=500)
    RecordCount = serializers.IntegerField()


class DiscountMasterFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    FromDate = serializers.DateField()
    ToDate = serializers.DateField()
    CustomerName = serializers.CharField(max_length=500)
    ItemName = serializers.CharField(max_length=500) 
    DiscountType = serializers.IntegerField()
    Discount = serializers.DecimalField(max_digits=20, decimal_places=2)
    Partytype = serializers.CharField(max_length=500)  
    PriceListName = serializers.CharField(max_length=500)  
    CreatedBy = serializers.IntegerField()
    CreatedOn = serializers.DateTimeField()