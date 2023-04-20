from ..models import *
from rest_framework import serializers
from ..Serializer.S_BankMaster import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *

# Return Save Serializers

class PurchaseReturnItemImageSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_PurchaseReturnItemImages
        fields = ['Item_pic']

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    ReturnItemImages = PurchaseReturnItemImageSerializer(many=True)
    class Meta :
        model= TC_PurchaseReturnItems
        fields = fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount','CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','ReturnItemImages']   
        

class PurchaseReturnSerializer(serializers.ModelSerializer):
    ReturnItems = PurchaseReturnItemsSerializer(many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = ['ReturnDate', 'ReturnNo', 'FullReturnNumber', 'GrandTotal', 'RoundOffAmount','ReturnReason', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'ReturnItems']
        
        
    def create(self, validated_data):
        ReturnItems_data = validated_data.pop('ReturnItems')
        PurchaseReturnID = T_PurchaseReturn.objects.create(**validated_data)
        
        for ReturnItem_data in ReturnItems_data:
            ReturnItemImages_data = ReturnItem_data.pop('ReturnItemImages')
            ReturnItemID =TC_PurchaseReturnItems.objects.create(PurchaseReturn=PurchaseReturnID, **ReturnItem_data)
            
            for ReturnItemImage_data in ReturnItemImages_data:
                ItemImages =TC_PurchaseReturnItemImages.objects.create(PurchaseReturnItem=ReturnItemID, **ReturnItemImage_data) 
        
        return PurchaseReturnID      
        
        

# Return List serializer

class PurchaseReturnSerializerSecond(serializers.ModelSerializer):
    ReturnReason = GeneralMasterserializer(read_only=True)
    Party = PartiesSerializer(read_only=True)
    Customer = PartiesSerializer(read_only=True)
    ReturnItems = PurchaseReturnItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'       