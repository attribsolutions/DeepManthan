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


class UserNameSerializer(serializers.CharField):
    def to_representation(self, value):
        user = M_Employees.objects.get(id=value)
        return user.Name if user else None

class PartyNameForLogSerializer(serializers.CharField):
    def to_representation(self, value):
        party = M_Parties.objects.get(id=value)
        return party.Name if party else None

class TransactionlogSerializer(serializers.ModelSerializer):
    UserName = UserNameSerializer(source='User')
    PartyName = PartyNameForLogSerializer(source='PartyID')
    class Meta:
        model = Transactionlog
        fields = ['TranasactionDate','UserName','IPaddress','TransactionType','TransactionID','PartyName']   

   