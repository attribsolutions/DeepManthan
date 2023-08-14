from rest_framework import serializers
from ..models import *
from ..Serializer.S_Drivers import  *
from ..Serializer.S_Vehicles import  *
from ..Serializer.S_Routes import  *
from ..Serializer.S_Parties import  *


class LoadingSheetListSerializer(serializers.ModelSerializer):
    Party = M_PartiesSerializerSecond()
    # Route = RouteSerializer()
    Driver = M_DriverSerializer()
    Vehicle = VehiclesSerializerSecond()
    class Meta:
        model = T_LoadingSheet
        fields = ['id', 'Date', 'No', 'Party', 'Route','TotalAmount', 'InvoiceCount', 'Vehicle', 'Driver', 'CreatedBy', 'UpdatedBy','CreatedOn', 'LoadingSheetDetails']

# Post and Put Methods Serializer

class LoadingSheetDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TC_LoadingSheetDetails
        fields = ['Invoice']

class LoadingSheetSerializer(serializers.ModelSerializer):
    LoadingSheetDetails = LoadingSheetDetailsSerializer(many=True)
    class Meta:
        model = T_LoadingSheet
        fields = ['id', 'Date', 'No', 'Party', 'Route','TotalAmount', 'InvoiceCount', 'Vehicle', 'Driver', 'CreatedBy', 'UpdatedBy','CreatedOn', 'LoadingSheetDetails']
        
    def create(self, validated_data):
     
        Vehicle = validated_data.get('Vehicle')
        Driver = validated_data.get('Driver')
     
        LoadingSheetDetails_data = validated_data.pop('LoadingSheetDetails')
        LoadingSheetID = T_LoadingSheet.objects.create(**validated_data)
        for LoadingSheet_data in LoadingSheetDetails_data:
            
            TC_LoadingSheetDetails.objects.create(LoadingSheet=LoadingSheetID, **LoadingSheet_data)
            InvoiceID = LoadingSheet_data.get('Invoice')
            InvoiceVehicleandDriverupdate=T_Invoices.objects.filter(id=InvoiceID.id).update(Vehicle = Vehicle,Driver = Driver)
        return LoadingSheetID 
       

class LoadingSheetInvoicesSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    InvoiceDate = serializers.DateField()
    Customer_id = serializers.IntegerField()
    FullInvoiceNumber =  serializers.CharField(max_length=500)
    GrandTotal = serializers.CharField(max_length=500)
    Party_id =  serializers.IntegerField()
    CreatedOn = serializers.CharField(max_length=500)
    UpdatedOn = serializers.EmailField(max_length=200)
    Name = serializers.CharField(max_length=500)
    
    
    
    
class LoadingSheetPrintSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    Item_id=serializers.IntegerField()
    Unit_id=serializers.IntegerField()
    ItemName=serializers.CharField(max_length=100)
    GroupTypeName=serializers.CharField(max_length=100)
    GroupName=serializers.CharField(max_length=100)
    SubGroupName=serializers.CharField(max_length=100)
    Quantity=serializers.DecimalField(max_digits=10, decimal_places=2)
    MRPValue=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount=serializers.DecimalField(max_digits=10, decimal_places=2)
    BatchCode = serializers.CharField(max_length=100)  
    QtyInBox = serializers.DecimalField(max_digits=10, decimal_places=3)
    QtyInNo = serializers.DecimalField(max_digits=10, decimal_places=3)
     
        
        