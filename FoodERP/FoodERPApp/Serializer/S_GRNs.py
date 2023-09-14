from ..models import *
from rest_framework import serializers
from collections import OrderedDict
from ..Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from .S_GSTHSNCode import *
from .S_Orders import * 

class Partiesserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id', 'Name']
        
''' POST AND PUT Methods Serializers  Save/Edit  Create/Update '''
class O_BatchWiseLiveStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['Item','Quantity','Unit','OriginalBaseUnitQuantity','BaseUnitQuantity','Party','CreatedBy']
    
class O_LiveBatchesSerializer(serializers.ModelSerializer):
    
    O_BatchWiseLiveStockList = O_BatchWiseLiveStockSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','GST','Rate','BatchDate', 'BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList','GSTPercentage','MRPValue']
    


class TC_GRNReferencesSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = TC_GRNReferences
        fields = ['Invoice', 'Order', 'ChallanNo','Inward','Challan']        

class TC_GRNItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_GRNItems
        fields = ['Item', 'Quantity', 'Unit', 'BaseUnitQuantity', 'MRP', 'ReferenceRate', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount',
                  'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode','SystemBatchCode','SystemBatchDate','GSTPercentage','MRPValue','QtyInBox','QtyInKg','QtyInNo','ActualQuantity']

class T_GRNSerializer(serializers.ModelSerializer):

    GRNItems = TC_GRNItemsSerializer(many=True)
    
    O_LiveBatchesList=O_LiveBatchesSerializer(many=True)
    
    GRNReferences = TC_GRNReferencesSerializer(many=True) 
    class Meta:
        model = T_GRNs
        fields = ['GRNDate', 'Customer', 'GRNNumber', 'FullGRNNumber','InvoiceNumber','GrandTotal', 'Party', 'CreatedBy', 'UpdatedBy', 'GRNItems','O_LiveBatchesList','GRNReferences']
       
    def create(self, validated_data):
       
        GRNItems_data = validated_data.pop('GRNItems')
        O_LiveBatchesLists_data=validated_data.pop('O_LiveBatchesList')
        
        GRNReferences_data = validated_data.pop('GRNReferences')
        
        
        grnID = T_GRNs.objects.create(**validated_data)
        
        for GRNItem_data in GRNItems_data :
            # print(grnID)
            GrnItem=TC_GRNItems.objects.create(GRN=grnID, **GRNItem_data)
 
        for O_LiveBatchesList_data in O_LiveBatchesLists_data :
            O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
            BatchID=O_LiveBatches.objects.create(**O_LiveBatchesList_data)
            for O_BatchWiseLiveStockList in O_BatchWiseLiveStockLists:
                O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(GRN=grnID,LiveBatche=BatchID,**O_BatchWiseLiveStockList)  
            
        
        # for GRNReference_data in GRNReferences_data:
            
            
        #     a=str(GRNReference_data['Order']) 
        #     OrderID=re.findall(r'\d+', a)
        #     GRNReferences=TC_GRNReferences.objects.create(GRN=grnID, **GRNReference_data)
        
        for GRNReference_data in GRNReferences_data:
            GRNReferences=TC_GRNReferences.objects.create(GRN=grnID, **GRNReference_data)
            
       
        return grnID
      

    def update(self, instance, validated_data):

        instance.GRNDate = validated_data.get(
            'GRNDate', instance.GRNDate)
        instance.Customer = validated_data.get(
            'Customer', instance.Customer)
        instance.Party = validated_data.get(
            'Party', instance.Party)

        instance.GrandTotal = validated_data.get(
            'GrandTotal', instance.GrandTotal)
       
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy)

        instance.save()

        for items in instance.GRNItems.all():
            items.delete()

        for items in instance.GRNReferences.all():
            items.delete()

        for GRNReference_data in validated_data['GRNReferences']:
            Reference_data = TC_GRNReferences.objects.create(
                GRN=instance, **GRNReference_data)

        for GRNItem_data in validated_data['GRNItems']:
            TC_GRNItemsID = TC_GRNItems.objects.create(
                GRN=instance, **GRNItem_data)
        return instance




'''Single Record Details Fetch Get Methods Serializer '''


class Partiesserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id', 'Name']

class TC_GRNReferencesSerializerSecond(serializers.ModelSerializer):
    Order = T_OrderSerializerThird(read_only=True)
    class Meta:
        model = TC_GRNReferences
        fields = ['Invoice', 'Order', 'ChallanNo','Inward', 'Challan'] 
        
class ItemSerializer(serializers.ModelSerializer):
    class Meta : 
        model = M_Items
        fields = ['id','Name']

class Unitserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['Name']

class UnitSerializerSecond(serializers.ModelSerializer):
    UnitID= serializers.SlugRelatedField(read_only=True,slug_field='Name')
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID','BaseUnitConversion']          

class TC_GRNItemsSerializerSecond(serializers.ModelSerializer):
    
    Item=ItemSerializer(read_only=True)
    Unit=UnitSerializerSecond(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    MRP = M_MRPsSerializer(read_only=True)
    class Meta:
        model = TC_GRNItems
        fields = ['Item', 'Quantity', 'Unit', 'BaseUnitQuantity', 'MRP', 'ReferenceRate', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount',
                  'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode','SystemBatchCode','SystemBatchDate','MRPValue','GSTPercentage']          

    
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(TC_GRNItemsSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("GST", None):
            ret["GST"] = {"id": None, "GSTPercentage": None}
            
        if not ret.get("MRP", None):
            ret["MRP"] = {"id": None, "MRP": None}    
        return ret

class T_GRNSerializerForGET(serializers.ModelSerializer):
    Customer = Partiesserializer(read_only=True)
    Party = Partiesserializer(read_only=True)
    GRNReferences = TC_GRNReferencesSerializerSecond(many=True,read_only=True)
    GRNItems = TC_GRNItemsSerializerSecond(many=True)

    class Meta:
        model = T_GRNs
        fields = ['id', 'GRNDate', 'Customer', 'GRNNumber', 'FullGRNNumber','InvoiceNumber','GrandTotal', 'Party', 'CreatedBy', 'UpdatedBy','CreatedOn', 'GRNReferences', 'GRNItems']
