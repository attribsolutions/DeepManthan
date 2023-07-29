
from ..models import *
from rest_framework import serializers

class PartyDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    MobileNo = serializers.CharField(max_length=500)
    Address =serializers.CharField(max_length=500)
    FSSAINo =serializers.CharField(max_length=500)
    GSTIN = serializers.CharField(max_length=500)


class ClaimSummarySerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    ReturnDate=serializers.DateField()
    FullReturnNumber = serializers.CharField(max_length=500)
    CustomerName=serializers.CharField(max_length=500)
    ItemName = serializers.CharField(max_length=500)
    MRP = serializers.DecimalField(max_digits=10, decimal_places=2)
    Quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    GST = serializers.DecimalField(max_digits=10, decimal_places=2)
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)       
    CGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    ApprovedQuantity =  serializers.DecimalField(max_digits=10, decimal_places=2)
    Discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=10, decimal_places=2)


        