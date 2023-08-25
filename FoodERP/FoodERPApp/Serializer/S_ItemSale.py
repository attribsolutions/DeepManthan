from rest_framework import serializers
from ..models import *


class ItemSaleReportSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    InvoiceDate = serializers.DateField()
    SaleMadeFrom = serializers.CharField(max_length=500)
    SaleMadeTo = serializers.CharField(max_length=500)
    FullInvoiceNumber=serializers.CharField(max_length=100)
    SupplierName =serializers.CharField(max_length=100)
    RouteName =serializers.CharField(max_length=100)
    CustomerName=serializers.CharField(max_length=100)
    GroupName=serializers.CharField(max_length=100)
    SubGroupName=serializers.CharField(max_length=100)
    ItemName=serializers.CharField(max_length=100)
    QtyInKg =serializers.DecimalField(max_digits=20, decimal_places=2)
    QtyInNo =serializers.DecimalField(max_digits=20, decimal_places=2)
    QtyInBox =serializers.DecimalField(max_digits=20, decimal_places=2)
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)
    BasicAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount=serializers.DecimalField(max_digits=10, decimal_places=2)
    GrandTotal = serializers.DecimalField(max_digits=20, decimal_places=2)
    RoundOffAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    TCSAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    FullGRNNumber = serializers.CharField(max_length=500)
    
class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= M_PartyType
        fields = '__all__'    
    
class ItemSaleSupplierSerializer(serializers.ModelSerializer):
    PartyType=PartyTypeSerializer(read_only=True)

    class Meta:
        model =  M_Parties
        fields = ['id','Name','PartyType']
        
        
class ItemSaleItemSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
  

           
    
    