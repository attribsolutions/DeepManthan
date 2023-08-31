from ..models import *
from rest_framework import serializers
from ..Serializer.S_Items import *
from ..Serializer.S_Orders import  *
from ..Serializer.S_Drivers import  *
from ..Serializer.S_Vehicles import  *

# code by ankita 
# class RouteSerializer(serializers.ModelSerializer):
#     Name = serializers.CharField(max_length=500)
#     class Meta:
#         model = M_Routes
#         fields = '__all__'

# code by ankita 
# class MCPartySubPartySerializer(serializers.ModelSerializer):
#     Route= RouteSerializer()
#     class Meta:
#         model = MC_PartySubParty
#         fields = '__all__'
        
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
    # MCSubParty=MCPartySubPartySerializer(many=True) # code by ankita 
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email','PartyAddress','State','MobileNo','PartyType_id'] 

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
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(OrderserializerforInvoice, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Description", None):
            ret["Description"] = None  
            
        return ret    
       
       
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
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch','MRPValue','GSTPercentage','QtyInBox','QtyInKg','QtyInNo']   

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
        fields = ['id','InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party','Vehicle','Driver', 'InvoiceItems', 'InvoicesReferences', 'obatchwiseStock','TCSAmount']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        InvoicesReferences_data = validated_data.pop('InvoicesReferences')
        O_BatchWiseLiveStockItems_data = validated_data.pop('obatchwiseStock')
        InvoiceID = T_Invoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemID =TC_InvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                    raise serializers.ValidationError("Not In Stock ")    
          
        for InvoicesReference_data in InvoicesReferences_data:
          
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
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch','MRPValue','GSTPercentage','QtyInBox','QtyInKg','QtyInNo']
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(InvoiceItemsSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("MRP", None):
            ret["MRP"] = {"id": None, "MRP": None}
            
        if not ret.get("Margin", None):
            ret["Margin"] = {"id": None, "Margin": None} 
        
        if not ret.get("GST", None):
            ret["GST"] = {"id": None, "GSTPercentage": None, "HSNCode":None }        
             
        return ret    
class InvoiceUploadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InvoiceUploads
        fields=['AckNo','Irn','QRCodeUrl','EInvoicePdf','EwayBillNo','EwayBillUrl','EInvoiceIsCancel','EwayBillIsCancel']           

class InvoiceSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    InvoiceItems = InvoiceItemsSerializerSecond(many=True)
    InvoicesReferences = InvoicesReferencesSerializerSecond(many=True)
    Driver= M_DriverSerializer(read_only=True)
    Vehicle = VehiclesSerializer(read_only=True)
    InvoiceUploads=InvoiceUploadsSerializer(many=True)
    
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

        if not ret.get("Route", None):
            ret["Route"] = {"id": None, "Name": None}
        
        return ret          


class InvoiceSerializerThird(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    InvoiceItems = InvoiceItemsSerializerSecond(many=True)
    InvoicesReferences = InvoicesReferencesSerializerSecond(many=True)
    Driver= M_DriverSerializer(read_only=True)
    Vehicle = VehiclesSerializer(read_only=True)
    InvoiceUploads=InvoiceUploadsSerializer(many=True)
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
        
        
        
class ChildInvoiceItemSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    Item_id=serializers.IntegerField()
    ItemName=serializers.CharField(max_length=100)
    Quantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    MRP_id=serializers.IntegerField() 
    MRPValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)
    Unit_id=serializers.IntegerField() 
    UnitName=serializers.CharField(max_length=100)
    BaseUnitQuantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    GST_id=serializers.IntegerField()
    GSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    BasicAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount=serializers.DecimalField(max_digits=10, decimal_places=2) 
    BatchCode=serializers.CharField(max_length=100) 
    BatchDate = serializers.DateField()
    HSNCode=serializers.CharField(max_length=100)
    Discount = serializers.DecimalField(max_digits=20, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    QtyInNo = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInKg = models.DecimalField(max_digits=30, decimal_places=20)
    QtyInBox = models.DecimalField(max_digits=30, decimal_places=20)
   
#Invoice Serializer for TC_ReceiptInvoices
        
class GlobleInvoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = T_Invoices
        fields = ['id','InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'CreatedOn']                