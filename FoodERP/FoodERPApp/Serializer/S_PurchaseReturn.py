from ..models import *
from rest_framework import serializers
from ..Serializer.S_BankMaster import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_PurchaseReturnItems
        fields = '__all__'

class PurchaseReturnSerializer(serializers.ModelSerializer):
    PurchaseReturn = PurchaseReturnItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'