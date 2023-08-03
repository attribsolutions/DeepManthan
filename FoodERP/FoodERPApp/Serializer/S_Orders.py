from ..models import *
from rest_framework import serializers
from .S_Parties import * 
from .S_Items import * 
from .S_GSTHSNCode import * 
from .S_Margins import * 
from .S_Mrps import * 
from .S_TermsAndConditions import *

class M_POTypeserializer(serializers.ModelSerializer):
    class Meta : 
        model = M_POType
        fields = '__all__'

class M_POTypeserializerSecond(serializers.ModelSerializer):
    class Meta : 
        model = M_POType
        fields =  ['id', 'Name','Company', 'Division']

# POST Method
class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name','SAPPartyCode','PAN','GSTIN']
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(PartiesSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("PAN", None):
            ret["PAN"] = None  
            
        return ret 
    
class TC_OrderItemsSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = TC_OrderItems
        fields = ['Item','Quantity','MRP','Rate','Unit','BaseUnitQuantity','GST','Margin','BasicAmount','GSTAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','Amount','IsDeleted','Comment','MRPValue','GSTPercentage','QtyInBox','QtyInKg','QtyInNo','DiscountType','Discount','DiscountAmount']

class TC_OrderTermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=TC_OrderTermsAndConditions
        fields =['TermsAndCondition','IsDeleted']

class T_OrderSerializer(serializers.ModelSerializer):
    OrderItem = TC_OrderItemsSerializer(many=True)
    OrderTermsAndConditions=TC_OrderTermsAndConditionsSerializer(many=True)
    class Meta:
        model = T_Orders
        fields = ['id','OrderDate','DeliveryDate','Customer','Supplier','OrderNo','FullOrderNumber','OrderType','POType','Division','OrderAmount','Description','BillingAddress','ShippingAddress','CreatedBy', 'UpdatedBy','POFromDate','POToDate','IsConfirm','OrderItem','OrderTermsAndConditions']

    def create(self, validated_data):
        OrderItems_data = validated_data.pop('OrderItem')
        OrderTermsAndConditions_data = validated_data.pop('OrderTermsAndConditions')
        
        Order = T_Orders.objects.create(**validated_data)
        
        for OrderItem_data in OrderItems_data:
           TC_OrderItems.objects.create(Order=Order, **OrderItem_data)

        for OrderTermsAndCondition_data in OrderTermsAndConditions_data:
            TC_OrderTermsAndConditions.objects.create(Order=Order, **OrderTermsAndCondition_data)       
        
        return Order

    def update(self, instance, validated_data):
        
        # * Order Info
        
        instance.OrderDate = validated_data.get(
            'OrderDate', instance.OrderDate)   
        instance.DeliveryDate = validated_data.get(
            'DeliveryDate', instance.DeliveryDate)
        instance.POFromDate = validated_data.get(
            'POFromDate', instance.POFromDate)   
        instance.POToDate = validated_data.get(
            'POToDate', instance.POToDate)
        instance.POType = validated_data.get(
            'POType', instance.POType)          
        instance.OrderAmount = validated_data.get(
            'OrderAmount', instance.OrderAmount)
        instance.Description = validated_data.get(
            'Description', instance.Description)
        instance.BillingAddress = validated_data.get(
            'BillingAddress', instance.BillingAddress)
        instance.ShippingAddress = validated_data.get(
            'ShippingAddress', instance.ShippingAddress)
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy) 
                
        instance.save()

        # for items in instance.OrderItem.all():
        #     print(items.IsDeleted)
        #     SetFlag=TC_OrderItems.objects.filter(id=items.id).update(IsDeleted=1)
            
            
        # for items in instance.OrderTermsAndConditions.all():
            
        #     SetFlag=TC_OrderItems.objects.filter(id=items.id).update(IsDeleted=1)
            

        for OrderItem_data in validated_data['OrderItem']:
            if(OrderItem_data['Quantity'] == 0 and OrderItem_data['IsDeleted'] == 1 ) :
                SetFlag=TC_OrderItems.objects.filter(Item=OrderItem_data['Item'],Order=instance,IsDeleted=0).update(IsDeleted=1)
            elif(OrderItem_data['IsDeleted'] == 0 ) :
                SetFlag=TC_OrderItems.objects.filter(Item=OrderItem_data['Item'],Order=instance,IsDeleted=0)
                
                if SetFlag.count() == 0:
                    OrderItem_data['IsDeleted']=0
                    Items = TC_OrderItems.objects.create(Order=instance, **OrderItem_data)
            else: 
                SetFlag=TC_OrderItems.objects.filter(Item=OrderItem_data['Item'],Order=instance).update(IsDeleted=1)
                OrderItem_data['IsDeleted']=0
                Items = TC_OrderItems.objects.create(Order=instance, **OrderItem_data)
            
            
            
       
        for OrderTermsAndCondition_data in validated_data['OrderTermsAndConditions']:
            if(OrderTermsAndCondition_data['IsDeleted'] == 1 ) :
                SetFlag=TC_OrderTermsAndConditions.objects.filter(Order=instance).update(IsDeleted=1)
            else:
                TestExistance=TC_OrderTermsAndConditions.objects.filter(Order=instance ,TermsAndCondition=OrderTermsAndCondition_data['TermsAndCondition'])
                if TestExistance.count() == 0:
                    Items = TC_OrderTermsAndConditions.objects.create(Order=instance, **OrderTermsAndCondition_data)
       
 
        return instance  

class GRNReferanceSerializer(serializers.ModelSerializer):
    class Meta:
        model =TC_GRNReferences
        fields = ['Order','Inward']

class T_OrderSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Supplier = PartiesSerializerSecond(read_only=True)
    BillingAddress=PartyAddressSerializerSecond(read_only=True) 
    ShippingAddress=PartyAddressSerializerSecond(read_only=True) 
    OrderReferences= GRNReferanceSerializer(read_only=True,many=True)
    POType = M_POTypeserializer(read_only=True)
    class Meta:
        model = T_Orders
        fields = '__all__'
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(T_OrderSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("BillingAddress", None):
            ret["BillingAddress"] = {"id": None, "Address": None}
            
        if not ret.get("ShippingAddress", None):
            ret["ShippingAddress"] = {"id": None, "Address": None}    
        return ret    
        

class PartiesSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name','SAPPartyCode','GSTIN']


class UnitSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name','SAPPartyCode']
        
class Mc_ItemUnitSerializerThird(serializers.ModelSerializer):
    UnitID = UnitSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID','BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion']      
        
class TC_OrderItemSerializer(serializers.ModelSerializer):
    
    MRP = M_MRPsSerializer(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    Margin = M_MarginsSerializer(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta:
        model = TC_OrderItems
        fields = '__all__'
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(TC_OrderItemSerializer, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("MRP", None):
            ret["MRP"] = {"id": None, "MRP": None}
            
        if not ret.get("Margin", None):
            ret["Margin"] = {"id": None, "Margin": None}    
        return ret      



class TC_OrderTermsAndConditionsSerializer(serializers.ModelSerializer):
    TermsAndCondition=M_TermsAndConditionsSerializer(read_only=True)
    class Meta:
        model=TC_OrderTermsAndConditions
        fields ='__all__'



class T_OrderSerializerThird(serializers.ModelSerializer):
    Customer = PartiesSerializerThird(read_only=True)
    Supplier = PartiesSerializerThird(read_only=True)
    OrderItem = TC_OrderItemSerializer(read_only=True,many=True)
    POType = M_POTypeserializerSecond(read_only=True)
    
    OrderTermsAndConditions=TC_OrderTermsAndConditionsSerializer(many=True)
    BillingAddress=PartyAddressSerializerSecond(read_only=True) 
    ShippingAddress=PartyAddressSerializerSecond(read_only=True) 
    OrderReferences= GRNReferanceSerializer(read_only=True,many=True)
    class Meta:
        model = T_Orders
        fields = '__all__'


'''Order Serializer For Make Grn'''


# class PartiesSerializerForGrn(serializers.ModelSerializer):
#     class Meta:
#         model = M_Parties
#         fields = ['id','Name']
        
class OrderSerializerForGrn(serializers.Serializer):
    id=serializers.IntegerField()
    SupplierName = serializers.CharField(max_length=500)     
    OrderAmount=serializers.DecimalField(max_digits=20, decimal_places=2) 
    CustomerID =serializers.IntegerField() 

class OrderEditserializer(serializers.Serializer):
    # id=serializers.IntegerField()
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
    HSNCode=serializers.CharField(max_length=100)
    Margin_id=serializers.IntegerField() 
    MarginValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    BasicAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    GSTAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    CGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    IGSTPercentage=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount=serializers.DecimalField(max_digits=10, decimal_places=2)  
    Comment=serializers.CharField(max_length=100) 
    SAPItemCode=serializers.CharField(max_length=100)
    SAPUnitName=serializers.CharField(max_length=100)
    GroupTypeName=serializers.CharField(max_length=100) 
    GroupName=serializers.CharField(max_length=100)
    SubGroupName=serializers.CharField(max_length=100)
    DiscountType = serializers.CharField(max_length=500)
    Discount = serializers.DecimalField(max_digits=20, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    StockQuantity = serializers.DecimalField(max_digits=20, decimal_places=3)
   

class ReportOrderItemSerializer(serializers.ModelSerializer):
    Item = ItemSerializerSecond(read_only=True)
    class Meta:
        model = TC_OrderItems
        fields = '__all__'
        
    
class SummaryReportOrderSerializer(serializers.ModelSerializer):
    Customer = PartiesSerializerThird(read_only=True)
    Supplier = PartiesSerializerThird(read_only=True)
    OrderItem = ReportOrderItemSerializer(read_only=True,many=True)
    class Meta:
        model = T_Orders
        fields = '__all__'

    
class TestGRNReferanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_GRNReferences
        fields = '__all__'
        
class TestTermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta : 
        model = M_TermsAndConditions
        fields = '__all__'

class TestOrderTermsAndConditionsSerializer(serializers.ModelSerializer):
    # TermsAndCondition = TestTermsAndConditionsSerializer(read_only=True)
    class Meta:
        model = TC_OrderTermsAndConditions
        fields = ['id','TermsAndCondition']

    def to_representation(self, instance):
        data = super(TestOrderTermsAndConditionsSerializer,self).to_representation(instance)
        data['id'] = instance.TermsAndCondition.id
        data['TermsAndCondition'] = instance.TermsAndCondition.Name
        
        return data 


class TestPartyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyAddress
        fields = '__all__'


class TestPOTypeserializer(serializers.ModelSerializer):
    class Meta:
        model = M_POType
        fields = '__all__'


class TestPartiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = '__all__'


class TestMRPsSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_MRPMaster
        fields = '__all__'


class TestGstHsnCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = M_GSTHSNCode
        fields = '__all__'


class TestMarginsSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_MarginMaster
        fields = '__all__'


class TestItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = '__all__'


class TestUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = '__all__'


class TestMCItemUnitSerializer(serializers.ModelSerializer):
    UnitID = TestUnitSerializer(read_only=True)

    class Meta:
        model = MC_ItemUnits
        fields = '__all__'


class TestOrderItemSerializer(serializers.ModelSerializer):

    MRP = TestMRPsSerializer(read_only=True)
    GST = TestGstHsnCodeSerializer(read_only=True)
    Margin = TestMarginsSerializer(read_only=True)
    Item = TestItemsSerializer(read_only=True)
    Unit = TestMCItemUnitSerializer(read_only=True)

    class Meta:
        model = TC_OrderItems
        fields = '__all__'

    def to_representation(self, instance):
        # get representation from ModelSerializer
        data = super(TestOrderItemSerializer, self).to_representation(instance)

        if not data.get("MRP", None):
            data['MRP'] = None
            data['MRPValue'] = None
        else:
            data['MRP'] = instance.MRP.id
            data['MRPValue'] = instance.MRP.MRP

        data['GST'] = instance.GST.id
        data['GSTPercentage'] = instance.GST.GSTPercentage

        if not data.get("Margin", None):
            data['Margin'] = None
            data['MarginValue'] = None
        else:
            data['Margin'] = instance.Margin.id
            data['MarginValue'] = instance.Margin.Margin

        data['Item'] = instance.Item.id
        data['ItemName'] = instance.Item.Name
        data['Unit'] = instance.Unit.id
        data['UnitName'] = instance.Unit.UnitID.Name

        return data


class TestOrderSerializer(serializers.ModelSerializer):
    Customer = TestPartiesSerializer(read_only=True)
    Supplier = TestPartiesSerializer(read_only=True)
    OrderItem = TestOrderItemSerializer(read_only=True, many=True)
    POType = TestPOTypeserializer(read_only=True)
    OrderTermsAndConditions = TestOrderTermsAndConditionsSerializer(many=True)
    BillingAddress = TestPartyAddressSerializer(read_only=True)
    ShippingAddress = TestPartyAddressSerializer(read_only=True)

    class Meta:
        model = T_Orders
        fields = '__all__'

    def to_representation(self, instance):
        data = super(TestOrderSerializer, self).to_representation(instance)
        data['Customer'] = instance.Customer.id
        data['CustomerName'] = instance.Customer.Name
        data['Supplier'] = instance.Supplier.id
        data['SupplierName'] = instance.Supplier.Name
        data['POType'] = instance.POType.id
        data['POTypeName'] = instance.POType.Name
        data['BillingAddressID'] = instance.BillingAddress.id
        data['BillingAddress'] = instance.BillingAddress.Address
        data['ShippingAddressID'] = instance.ShippingAddress.id
        data['ShippingAddress'] = instance.ShippingAddress.Address

        return data
     


    