from dataclasses import fields
from ..models import *
from rest_framework import serializers



class H_ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = H_Modules
        fields = '__all__'

# class H_SubModulesSerializer(serializers.ModelSerializer):
#     Module=H_ModulesSerializer()
    
#     class Meta:
#         model = H_SubModules
#         fields = '__all__'
#         fields=['ID','Name','Icon','IsActive','DisplayIndex','Module']


                       