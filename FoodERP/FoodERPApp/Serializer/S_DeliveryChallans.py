from dataclasses import field
from ..models import *
from rest_framework import serializers


''' POST AND PUT Methods Serializers  Save/Edit  Create/Update '''

class TC_DeliveryReferencesSerializer(serializers.ModelSerializer):
    class Meta : 
        model=TC_DeliveryChallanReferences
        fields =['GRN']

class TC_DeliveryChallanItemsSerializer(serializers.ModelSerializer):
    class Meta : 
        model=TC_DeliveryChallanItems
        fields =['id','Item','Quantity','Unit','BaseUnitQuantity','MRP','ReferenceRate','Rate','BasicAmount','TaxType','GSTPercentage','GSTAmount','Amount','DiscountType','Discount','DiscountAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','BatchDate','BatchCode']
        
class T_DeliveryChallanSerializer(serializers.ModelSerializer):
    
    DeliveryChallanReferences=TC_DeliveryReferencesSerializer(many=True)
    DeliveryChallanItems=TC_DeliveryChallanItemsSerializer(many=True)
    
    class Meta:
        model =   T_DeliveryChallans
        fields = ['id','ChallanDate','Customer','ChallanNumber','FullChallanNumber', 'GrandTotal','Party','CreatedBy','UpdatedBy','DeliveryChallanReferences','DeliveryChallanItems']
        

    def create(self, validated_data):
        DeliveryChallanItems_data = validated_data.pop('DeliveryChallanItems')
        DeliveryChallanReferences_data = validated_data.pop('DeliveryChallanReferences')
        DeliveryChallanID = T_DeliveryChallans.objects.create(**validated_data)
       
        for DeliveryChallanReference_data in DeliveryChallanReferences_data:
            DeliveryChallanReferencedata=TC_DeliveryChallanReferences.objects.create(DeliveryChallan=DeliveryChallanID, **DeliveryChallanReference_data)

        for DeliveryChallanItem_data in DeliveryChallanItems_data:
            DeliveryChallanItemID =TC_DeliveryChallanItems.objects.create(DeliveryChallan=DeliveryChallanID, **DeliveryChallanItem_data)
        return DeliveryChallanID     

    def update(self, instance, validated_data):
        
        instance.ChallanDate = validated_data.get(
            'ChallanDate', instance.ChallanDate)
        instance.Customer = validated_data.get(
            'Customer', instance.Customer)
        instance.Party = validated_data.get(
            'Party', instance.Party) 
        instance.GrandTotal = validated_data.get(
            'GrandTotal', instance.GrandTotal)
        instance.ChallanNumber = validated_data.get(
            'ChallanNumber', instance.ChallanNumber) 
        instance.FullChallanNumber = validated_data.get(
            'FullChallanNumber', instance.FullChallanNumber)    
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy)  
         
        instance.save()
        
        for items in instance.DeliveryChallanItems.all():
            items.delete()

        for items in instance.DeliveryChallanReferences.all():
            items.delete()    
        
        for DeliveryChallanReference_data in validated_data['DeliveryChallanReferences']:
            Referencedata=TC_DeliveryChallanReferences.objects.create(DeliveryChallan=instance, **DeliveryChallanReference_data)
       
        for DeliveryChallanItem_data in validated_data['DeliveryChallanItems']:
            DeliveryChallanItemID = TC_DeliveryChallanItems.objects.create(DeliveryChallan=instance, **DeliveryChallanItem_data)
        return instance   

'''Single Record Details Fetch Get Methods Serializer '''

class Partiesserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id', 'Name']
        
class Unitserializer(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['Name']

class MC_ItemUnitsSerializer(serializers.ModelSerializer):
    UnitID= serializers.SlugRelatedField(read_only=True,slug_field='Name')
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID'] 
        
class ItemSerializer(serializers.ModelSerializer):
    class Meta : 
        model = M_Items
        fields = ['id','Name']
            
class TC_DeliveryChallanItemsSerializerSecond(serializers.ModelSerializer):
    
    Item=ItemSerializer(read_only=True)
    Unit=MC_ItemUnitsSerializer(read_only=True)
    class Meta:
        model = TC_GRNItems
        fields = ['Item', 'Quantity', 'Unit', 'BaseUnitQuantity', 'MRP', 'ReferenceRate', 'Rate', 'BasicAmount', 'TaxType', 'GSTPercentage', 'GSTAmount',
                  'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'BatchDate', 'BatchCode']                  
        
class T_DeliveryChallanSerializerForGET(serializers.ModelSerializer):
    Customer = Partiesserializer(read_only=True)
    Party = Partiesserializer(read_only=True)
    DeliveryChallanReferences = TC_DeliveryReferencesSerializer(many=True,read_only=True)
    DeliveryChallanItems = TC_DeliveryChallanItemsSerializerSecond(many=True)

    class Meta:
        model = T_GRNs
        fields = ['id','ChallanDate','Customer','ChallanNumber','FullChallanNumber', 'GrandTotal','Party','CreatedBy','UpdatedBy','DeliveryChallanReferences','DeliveryChallanItems']      