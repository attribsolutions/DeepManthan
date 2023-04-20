from ..models import *
from rest_framework import serializers
from ..Serializer.S_BankMaster import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *

# Return Save Serializers

class PurchaseReturnItemImageSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_PurchaseReturnItemImages
        fields = '__all__'

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    ReturnItemImages = PurchaseReturnItemImageSerializer(read_only=True,many=True)
    class Meta :
        model= TC_PurchaseReturnItems
        fields = '__all__'
        

class PurchaseReturnSerializer(serializers.ModelSerializer):
    ReturnItems = PurchaseReturnItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'
        

# Return List serializer

class PurchaseReturnSerializerSecond(serializers.ModelSerializer):
    ReturnReason = GeneralMasterserializer(read_only=True)
    Party = PartiesSerializer(read_only=True)
    Customer = PartiesSerializer(read_only=True)
    ReturnItems = PurchaseReturnItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'       