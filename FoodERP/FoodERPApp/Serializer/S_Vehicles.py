from ..models import *
from rest_framework import serializers


class M_VehiclesSerializerList(serializers.Serializer):
    id = serializers.IntegerField()
    VehicleNumber = serializers.CharField(max_length=500)
    Description = serializers.CharField(max_length=500)
    DriverName = serializers.CharField(max_length=500)
    Vehicletype = serializers.CharField(max_length=500)

class DriverSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Drivers
        fields = ['id','Name']
               
class VehicleTypesSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_VehicleTypes
        fields = ['id','Name']  
        
'''      POST Method Serializer      '''


class M_VehiclesSerializer(serializers.ModelSerializer):

    class Meta :
        model= M_Vehicles
        fields = ['VehicleNumber' , 'Description', 'Driver', 'VehicleType']
    
    def create(self, validated_data):
        VehicleDivisions_data = validated_data.pop('VehicleDivisions')
        VehicleID= M_Vehicles.objects.create(**validated_data)
        
        return VehicleID
    
    def update(self, instance, validated_data):
    
        instance.VehicleNumber = validated_data.get(
            'VehicleNumber', instance.VehicleNumber)
        instance.Description = validated_data.get(
            'Description', instance.Description)
        instance.Driver = validated_data.get(
            'Driver', instance.Driver)
        instance.VehicleType = validated_data.get(
            'VehicleType', instance.VehicleType)
            
        instance.save()
        
        for a in instance.VehicleDivisions.all():
            a.delete()
                        
       
        return instance
        
                
''' GET Method Single Data  Serializers''' 
class DivisionSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name']
                    
class VehiclesSerializerSecond(serializers.ModelSerializer):
    Driver = DriverSerializer()
    VehicleType= VehicleTypesSerializer()
    class Meta :
        model= M_Vehicles
        fields = '__all__'    
                          
                                  
        