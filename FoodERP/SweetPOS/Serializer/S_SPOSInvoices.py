from ..models import *
from rest_framework import serializers



class SPOSInvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_SPOSInvoiceItems
        fields = '__all__'



class SPOSInvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = SPOSInvoiceItemsSerializer(many=True)
    
    class Meta:
        model = T_SPOSInvoices
        fields = ['id','InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party','Vehicle','Driver', 'InvoiceItems', 'InvoicesReferences', 'obatchwiseStock','TCSAmount']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        
        InvoiceID = T_SPOSInvoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemID =TC_SPOSInvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        
        return InvoiceID   
