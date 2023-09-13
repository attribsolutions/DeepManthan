from rest_framework import serializers
from ..models import *

class EmplyoeeSerializerSecond(serializers.ModelSerializer):
    Name = serializers.SerializerMethodField()
    class Meta:
        model =  M_Users
        fields = ['id','Name']

    def get_Name(self, obj):
        return obj.Employee.Name if obj.Employee else None
    

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_TransactionType
        fields = '__all__'