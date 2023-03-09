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
        fields = ['id', 'VehicleNumber' , 'Description', 'VehicleType', 'Party', 'Company', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn']
          
        