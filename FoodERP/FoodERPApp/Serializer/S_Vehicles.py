from ..models import *
from rest_framework import serializers

               
class VehicleTypesSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_VehicleTypes
        fields = ['id','Name']  
        
'''      POST Method Serializer      '''


class VehiclesSerializer(serializers.ModelSerializer):
    VehicleType= VehicleTypesSerializer()
    class Meta :
        model= M_Vehicles
        fields = ['id', 'VehicleNumber' , 'Description', 'VehicleType', 'Party', 'Company', 'CreatedBy', 'UpdatedBy']
    
    def create(self, validated_data):
        VehicleID= M_Vehicles.objects.create(**validated_data)
        
        return VehicleID
    
    def update(self, instance, validated_data):
    
        instance.VehicleNumber = validated_data.get(
            'VehicleNumber', instance.VehicleNumber)
        instance.Description = validated_data.get(
            'Description', instance.Description)
        instance.VehicleType = validated_data.get(
            'VehicleType', instance.VehicleType)    
        instance.save()
        
        return instance
          
        