from ..Serializer.S_Invoices import Mc_ItemUnitSerializerThird

from ..models import *
from rest_framework import serializers
from ..Serializer.S_BankMaster import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *

# Return Save Serializers
class O_BatchWiseLiveStockReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['Item','Quantity','Unit','OriginalBaseUnitQuantity','BaseUnitQuantity','Party','IsDamagePieces','CreatedBy']
    
class O_LiveBatchesReturnSerializer(serializers.ModelSerializer):
    
    O_BatchWiseLiveStockList = O_BatchWiseLiveStockReturnSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','MRPValue','GST','GSTPercentage','Rate','BatchDate', 'BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList']
    

class PurchaseReturnItemImageSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_PurchaseReturnItemImages
        fields = ['Item_pic']

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    ReturnItemImages = PurchaseReturnItemImageSerializer(many=True)
    
    class Meta :
        model= TC_PurchaseReturnItems
        fields = fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount','CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','ReturnItemImages','MRPValue','GSTPercentage','ItemReason','Comment','ApprovedQuantity']   
        
class PurchaseReturnReferences(serializers.ModelSerializer):
    class Meta :
        model = TC_PurchaseReturnReferences
        fields =["SubReturn"]

class PurchaseReturnSerializer(serializers.ModelSerializer):
    ReturnItems = PurchaseReturnItemsSerializer(many=True)
    O_LiveBatchesList=O_LiveBatchesReturnSerializer(many=True)
    PurchaseReturnReferences=PurchaseReturnReferences(many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = ['ReturnDate', 'ReturnNo', 'FullReturnNumber', 'GrandTotal', 'RoundOffAmount','ReturnReason', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party','IsApproved', 'Comment', 'ReturnItems','O_LiveBatchesList','PurchaseReturnReferences']
        
        
    def create(self, validated_data):
        Mode = validated_data.pop('Mode')
        ReturnItems_data = validated_data.pop('ReturnItems')
        O_LiveBatchesLists_data=validated_data.pop('O_LiveBatchesList')
        PurchaseReturnReferences_data=validated_data.pop('PurchaseReturnReferences')
        PurchaseReturnID = T_PurchaseReturn.objects.create(**validated_data)
        
        for ReturnItem_data in ReturnItems_data:
            ReturnItemImages_data = ReturnItem_data.pop('ReturnItemImages')
            ReturnItemID =TC_PurchaseReturnItems.objects.create(PurchaseReturn=PurchaseReturnID, **ReturnItem_data)
            
            for ReturnItemImage_data in ReturnItemImages_data:
                ItemImages =TC_PurchaseReturnItemImages.objects.create(PurchaseReturnItem=ReturnItemID, **ReturnItemImage_data) 
        
        if PurchaseReturnReferences_data : 
            for PurchaseReturnReference_data in PurchaseReturnReferences_data:
                ReturnReference=TC_PurchaseReturnReferences.objects.create(PurchaseReturn=PurchaseReturnID, **PurchaseReturnReference_data)
        
        for O_LiveBatchesList_data in O_LiveBatchesLists_data :
            O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
            BatchID=O_LiveBatches.objects.create(**O_LiveBatchesList_data)
            for O_BatchWiseLiveStockList in O_BatchWiseLiveStockLists:
                O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(PurchaseReturn=PurchaseReturnID,LiveBatche=BatchID,**O_BatchWiseLiveStockList)  
        
        if Mode == 3: #  Sales Return Consoldated Item qty minus from O_batchwise when send to supplier
            for O_LiveBatchesList_data in O_LiveBatchesLists_data :
                O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
                for O_BatchWiseLiveStockList in O_BatchWiseLiveStockLists:
                    OBatchQuantity=O_BatchWiseLiveStock.objects.filter(Item=O_BatchWiseLiveStockList[0]['Item'],PurchaseReturn=O_BatchWiseLiveStockList[0]['PurchaseReturn'],Unit=O_BatchWiseLiveStockList[0]['Unit']).values('BaseUnitQuantity')
                    if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockList['BaseUnitQuantity']):
                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(Item=O_BatchWiseLiveStockList[0]['Item'],PurchaseReturn=O_BatchWiseLiveStockList[0]['PurchaseReturn'],Unit=O_BatchWiseLiveStockList[0]['Unit']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockList['BaseUnitQuantity'])
                            
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
     
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(PurchaseReturnSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("ReturnReason", None):
            ret["ReturnReason"] = {"id": None, "Name": None}
              
        return ret    
    
class ItemsReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model= M_GeneralMaster
        fields= ['id','Name']

class M_ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model= M_Items
        fields= ['id','Name']

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    Item = M_ItemsSerializer()
    ItemReason = ItemsReasonSerializer()
    Unit=Mc_ItemUnitSerializerThird()
    class Meta :
        model= TC_PurchaseReturnItems
        fields = '__all__'

    
class PurchaseReturnSerializerThird(serializers.ModelSerializer):
    ReturnItems = PurchaseReturnItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'

    def create(self, validated_data):
        ReturnItems_data = validated_data.pop('ReturnItems')
        PurchaseReturnID = T_PurchaseReturn.objects.create(**validated_data)
        
        for a in ReturnItems_data:
            ReturnItemID =TC_PurchaseReturnItems.objects.create(PurchaseReturn=PurchaseReturnID, **a)
            
        return PurchaseReturnID      
    


class PurchaseReturnItemsSerializer2(serializers.ModelSerializer):
    Item=M_ItemsSerializer(read_only=True)
    ItemReason = GeneralMasterserializer(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta :
        model= TC_PurchaseReturnItems
        fields = '__all__'    


