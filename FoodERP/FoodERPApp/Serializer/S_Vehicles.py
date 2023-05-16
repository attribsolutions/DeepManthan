from ..models import *
from rest_framework import serializers
               
class VehicleTypesSerializerSecond(serializers.ModelSerializer):
    class Meta :
        model= M_VehicleTypes
        fields = ['id','Name','Company']  
        
'''      POST Method Serializer      '''

class VehiclesSerializerSecond(serializers.ModelSerializer):
    VehicleType= VehicleTypesSerializerSecond()
    class Meta :
        model= M_Vehicles
        fields = ['id', 'VehicleNumber' , 'Description', 'VehicleType', 'Party', 'Company', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn']
          
class VehiclesSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Vehicles
        fields = ['id', 'VehicleNumber' , 'Description', 'VehicleType', 'Party', 'Company', 'CreatedBy','UpdatedBy']        