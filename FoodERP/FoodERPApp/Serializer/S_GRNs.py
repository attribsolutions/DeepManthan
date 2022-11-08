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
        fields =['BatchDate','BatchCode','Quantity','MRP','Item','Unit']

class TC_GRNItemsSerializer(serializers.ModelSerializer):
    GRNItemBatches=TC_GRNItemBatchesSerializer(many=True)
    class Meta : 
        model=TC_GRNItems
        fields =['Item','Quantity','Unit','BaseUnitQuantity','MRP','ReferenceRate','Rate','BasicAmount','TaxType','GSTPercentage','GSTAmount','Amount','DiscountType','Discount','DiscountAmount','CGST','SGST','IGST','CGSTPercentage','SGSTPercentage','IGSTPercentage','GRNItemBatches']
        
        

class T_GRNSerializer(serializers.ModelSerializer):
    
    GRNReferences=TC_GRNReferencesSerializer(many=True)
    GRNItems=TC_GRNItemsSerializer(many=True)
    
    
    class Meta:
        model =   T_GRNs
        fields = ['GRNDate','Customer','GRNNumber','GrandTotal','Party','CreatedBy','UpdatedBy','GRNReferences','GRNItems']
        

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
        
        instance.Order = validated_data.get(
            'Order', instance.Order)
        instance.Customer = validated_data.get(
            'Customer', instance.Customer)
        instance.Party = validated_data.get(
            'Party', instance.Party)
        instance.GrandTotal = validated_data.get(
            'GrandTotal', instance.GrandTotal)
        instance.RoundOffAmount = validated_data.get(
            'RoundOffAmount', instance.RoundOffAmount)    
        instance.save()
        
        for items in instance.InvoiceItems.all():
            items.delete()
        
        for InvoiceItem_data in validated_data['InvoiceItems']:
            InvoiceItemBatches_data = InvoiceItem_data.pop('InvoiceItemBatches')
            TC_InvoiceItemsID = TC_InvoiceItems.objects.create(Invoice=instance, **InvoiceItem_data)
            for InvoiceItemBatch_data in InvoiceItemBatches_data:
               TC_InvoiceItemBatches.objects.create(Invoice=instance,InvoiceItem=TC_InvoiceItemsID, **InvoiceItemBatch_data)
        return instance     