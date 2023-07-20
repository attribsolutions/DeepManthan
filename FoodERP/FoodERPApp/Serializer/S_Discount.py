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
    Discount = serializers.IntegerField() 
    GroupTypeName = serializers.CharField(max_length=500)
    GroupName = serializers.CharField(max_length=500)
    SubGroupName = serializers.CharField(max_length=500)