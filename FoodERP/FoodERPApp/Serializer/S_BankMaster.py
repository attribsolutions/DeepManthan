from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Bank
        fields = '__all__'

class PartyBanksSerializer(serializers.ModelSerializer):
    Bank = BankSerializer(read_only=True)
    class Meta:
        model = MC_PartyBanks
        fields = '__all__'
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        data = super(PartyBanksSerializer, self).to_representation(instance)
        data['Bank'] = instance.Bank.id
        data['BankName'] = instance.Bank.Name
        return data
    
class PartyBanksSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyBanks
        fields = '__all__'                


         
        