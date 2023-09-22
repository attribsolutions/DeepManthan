from rest_framework import serializers
from ..models import *
from datetime import datetime


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
            

class TransactionlogSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    TransactionDate = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    UserName = serializers.CharField(max_length=500)
    IPaddress = serializers.CharField(max_length=500)
    TransactionType = serializers.CharField(max_length=500)
    TransactionID = serializers.IntegerField(default=1)
    PartyName = serializers.CharField(max_length=500)
    TransactionDetails =  serializers.CharField(max_length=500)
 