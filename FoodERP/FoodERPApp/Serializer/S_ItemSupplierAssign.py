from rest_framework import serializers
from ..models import *

class ItemSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_ItemSupplier
        fields = '__all__'
        
        
class GETItemSupplierSerializer(serializers.Serializer):
    id= serializers.IntegerField()    
    ItemID= serializers.IntegerField()
    ItemName=serializers.CharField(max_length=500)
    GroupName=serializers.CharField(max_length=500)
    SubGroupName=serializers.CharField(max_length=500)
    Suppliers=serializers.CharField(max_length=500)
    PartyId=serializers.IntegerField()


        