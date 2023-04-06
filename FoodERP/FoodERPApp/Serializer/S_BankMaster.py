from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Bank
        fields = '__all__'

class BankSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_Bank
        fields = '__all__'

class BankSerializerSecond(serializers.ModelSerializer):
    BankMaster = BankSerializerSecond(read_only=True)
    class Meta:
        model = M_Bank
        fields = '__all__' 
        