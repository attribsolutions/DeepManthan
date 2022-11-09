from dataclasses import field
from ..models import *
from rest_framework import serializers

class TC_GRNReferencesSerializer(serializers.ModelSerializer):
    class Meta : 
        model=TC_GRNReferences
        fields =['Invoice','Order']

class TC_GRNItemBatchesSerializer(serializers.ModelSerializer):
    class Meta : 
        model=TC_GRNItemBatches
        fields =['id','BatchDate','BatchCode','Quantity','MRP','Item','Unit']

class TC_GRNItemsSerializer(serializers.ModelSerializer):
    GRNItemBatches=TC_GRNItemBatchesSerializer(many=True)
    class Meta : 
        model=TC_GRNItems
        fields =['id','Item','Quantity','Unit','BaseUnitQuantity','MRP','ReferenceRate','Rate','BasicAmount','TaxType','GSTPercentage','GSTAmount','Amount','DiscountType','Discount','DiscountAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','GRNItemBatches']
        
        

class T_GRNSerializer(serializers.ModelSerializer):
    
    GRNReferences=TC_GRNReferencesSerializer(many=True)
    GRNItems=TC_GRNItemsSerializer(many=True)
    
    
    class Meta:
        model =   T_GRNs
        fields = ['id','GRNDate','Customer','GRNNumber','GrandTotal','Party','CreatedBy','UpdatedBy','GRNReferences','GRNItems']
        

    def create(self, validated_data):
        GRNItems_data = validated_data.pop('GRNItems')
        GRNReferences_data = validated_data.pop('GRNReferences')
        grnID = T_GRNs.objects.create(**validated_data)
       
        for GRNReference_data in GRNReferences_data:
            Reference_data=TC_GRNReferences.objects.create(GRN=grnID, **GRNReference_data)

        for GRNItem_data in GRNItems_data:
            GRNItemBatches_data = GRNItem_data.pop('GRNItemBatches')
           
            GRNItemID =TC_GRNItems.objects.create(GRN=grnID, **GRNItem_data)
            for GRNItemBatch_data in GRNItemBatches_data:
               TC_GRNItemBatches.objects.create(GRN=grnID,GRNItem=GRNItemID, **GRNItemBatch_data)
        
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
        instance.GRNNumber = validated_data.get(
            'GRNNumber', instance.GRNNumber)    
        instance.UpdatedBy = validated_data.get(
            'UpdatedBy', instance.UpdatedBy)  
         
        instance.save()
        
        for items in instance.GRNItems.all():
            items.delete()

        for items in instance.GRNReferences.all():
            items.delete()    
        
        for GRNReference_data in validated_data['GRNReferences']:
            Reference_data=TC_GRNReferences.objects.create(GRN=instance, **GRNReference_data)
       
        for GRNItem_data in validated_data['GRNItems']:
            GRNItemBatches_data = GRNItem_data.pop('GRNItemBatches')
            TC_GRNItemsID = TC_GRNItems.objects.create(GRN=instance, **GRNItem_data)
            for GRNItemBatch_data in GRNItemBatches_data:
               TC_GRNItemBatches.objects.create(GRN=instance,GRNItem=TC_GRNItemsID, **GRNItemBatch_data)
        return instance     