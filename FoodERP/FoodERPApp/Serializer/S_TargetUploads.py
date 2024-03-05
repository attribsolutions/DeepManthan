from rest_framework import serializers
from ..models import *
from datetime import datetime



class TargetUploadsOneSerializer(serializers.ModelSerializer):
    class Meta:
        model = T_TargetUploads
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = '__all__'
        
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = '__all__'

class TargetUploadsSerializer(serializers.ModelSerializer):
    Party = PartySerializer(read_only=True)
    Item = ItemSerializer(read_only=True)
    
    class Meta:
        model = T_TargetUploads
        fields = '__all__'






