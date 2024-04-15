from ..models import *
from rest_framework import serializers


class UsersSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_SweetPOSUser
        fields = '__all__'
        
class RolesSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_SweetPOSRoles
        fields = '__all__'
        
        