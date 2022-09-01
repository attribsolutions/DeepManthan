from ..models import *
from rest_framework import serializers


class M_DriverSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Drivers
        fields = ['id','Name']
        
        
class M_VehicleTypesSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Drivers
        fields = ['id','Name']  

       
class M_VehiclesSerializerList(serializers.Serializer):
    id = serializers.IntegerField()
    VehicleNumber = serializers.CharField(max_length=500)
    Description = serializers.CharField(max_length=500)
    DriverName = serializers.CharField(max_length=500)
    Vehicletype = serializers.CharField(max_length=500)


class M_VehiclesSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Vehicles
        fields = '__all__'    
                          
        