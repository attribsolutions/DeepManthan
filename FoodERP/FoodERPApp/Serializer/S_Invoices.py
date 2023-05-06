from ..models import *
from rest_framework import serializers
from ..Serializer.S_Items import *
from ..Serializer.S_Orders import  *
from ..Serializer.S_Drivers import  *
from ..Serializer.S_Vehicles import  *

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_States
        fields = '__all__'
        
class MC_PartyAdressSerializer(serializers.ModelSerializer):
    Address = serializers.CharField() 
    class Meta:
        model = MC_PartyAddress
        fields = '__all__'
        
class PartiesSerializerSecond(serializers.ModelSerializer):
    PartyAddress=MC_PartyAdressSerializer(many=True)
    State = StateSerializer(read_only=True)
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email','PartyAddress','State']

class UnitSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class Mc_ItemUnitSerializerThird(serializers.ModelSerializer):
    UnitID = UnitSerializerThird(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID','BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion'] 
       
class LiveBatchSerializer(serializers.ModelSerializer):
    MRP = M_MRPsSerializer(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    class Meta:
        model =O_LiveBatches
        fields = '__all__'
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(LiveBatchSerializer, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("MRP", None):
            ret["MRP"] = {"id": None, "MRP": None}
            
        if not ret.get("GST", None):
            ret["GST"] = {"id": None, "GSTPercentage": None} 
            
        return ret       

class StockQtyserializerForInvoice(serializers.ModelSerializer):
    LiveBatche=LiveBatchSerializer(read_only=True)
    Unit = Mc_ItemUnitSerializerThird()
    Item =  ItemSerializerSecond()
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','BaseUnitQuantity','Party','LiveBatche','Unit'] 
         
class OrderserializerforInvoice(serializers.ModelSerializer):
    class Meta:
        model = T_Orders
        fields = '__all__'
       
       
class InvoicesReferencesSerializerSecond(serializers.ModelSerializer):
    Order = OrderserializerforInvoice(read_only=True)
    class Meta:
        model = TC_InvoicesReferences
        fields = '__all__'
    
        
class InvoicesReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InvoicesReferences
        fields = ['Order']         
         
class InvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_InvoiceItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch','MRPValue','GSTPercentage']   

class obatchwiseStockSerializer(serializers.ModelSerializer):
    class Meta:
        model=O_BatchWiseLiveStock
        fields=['Quantity','BaseUnitQuantity','Item']
        
class InvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = InvoiceItemsSerializer(many=True)
    InvoicesReferences = InvoicesReferencesSerializer(many=True) 
    obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model = T_Invoices
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'InvoiceItems', 'InvoicesReferences', 'obatchwiseStock']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        InvoicesReferences_data = validated_data.pop('InvoicesReferences')
        O_BatchWiseLiveStockItems_data = validated_data.pop('obatchwiseStock')
        InvoiceID = T_Invoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemID =TC_InvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                print(OBatchQuantity[0]['BaseUnitQuantity'],O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                    
                    raise serializers.ValidationError("Not In Stock ")    
          
        for InvoicesReference_data in InvoicesReferences_data:
            print(InvoiceID) 
            InvoicesReferences = TC_InvoicesReferences.objects.create(Invoice=InvoiceID, **InvoicesReference_data)   
              
        
        return InvoiceID   

class BulkInvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = InvoiceItemsSerializer(many=True)
    
    class Meta:
        model = T_Invoices
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'InvoiceItems']
        # fields ='__all__'
    
    def create(self, validated_data):

        InvoiceItems_data = validated_data.pop('InvoiceItems')
        InvoiceID = T_Invoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemID =TC_InvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        return InvoiceID        
    
    
class InvoiceItemsSerializerSecond(serializers.ModelSerializer):
    
    MRP = M_MRPsSerializer(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    # Margin = M_MarginsSerializer(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta:
        model = TC_InvoiceItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch','MRPValue','GSTPercentage']
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(InvoiceItemsSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("MRP", None):
            ret["MRP"] = {"id": None, "MRP": None}
            
        if not ret.get("Margin", None):
            ret["Margin"] = {"id": None, "Margin": None} 
        
        if not ret.get("GST", None):
            ret["GST"] = {"id": None, "GSTPercentage ": None}        
             
        return ret    
            
class InvoiceSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    InvoiceItems = InvoiceItemsSerializerSecond(many=True)
    InvoicesReferences = InvoicesReferencesSerializerSecond(many=True)
    Driver= M_DriverSerializer(read_only=True)
    Vehicle = VehiclesSerializer(read_only=True)
    class Meta:
        model = T_Invoices
        fields = '__all__'
    
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(InvoiceSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Driver", None):
            ret["Driver"] = {"id": None, "Name": None}
            
        if not ret.get("Vehicle", None):
            ret["Vehicle"] = {"id": None, "VehicleNumber": None}
        
        return ret          


class InvoiceSerializerThird(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    InvoiceItems = InvoiceItemsSerializerSecond(many=True)
    InvoicesReferences = InvoicesReferencesSerializerSecond(many=True)
    Driver= M_DriverSerializer(read_only=True)
    Vehicle = VehiclesSerializer(read_only=True)
    class Meta:
        model = T_Invoices
        fields = '__all__'
    
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(InvoiceSerializerThird, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Driver", None):
            ret["Driver"] = {"id": None, "Name": None}
            
        if not ret.get("Vehicle", None):
            ret["Vehicle"] = {"id": None, "VehicleNumber": None}
        
        return ret         
            

class InvoiceSerializerForDelete(serializers.ModelSerializer):
    InvoiceItems = InvoiceItemsSerializer(many=True)
 
    class Meta:
        model = T_Invoices
        fields = '__all__'   
        
#Invoice Serializer for TC_ReceiptInvoices
        
class GlobleInvoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = T_Invoices
        fields = ['id','InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'CreatedOn']                