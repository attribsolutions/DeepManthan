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
        
class TargetAchievementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Month = serializers.IntegerField()
    Year =serializers.IntegerField()
    PartyID = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=200)
    ItemName = serializers.CharField(max_length=200)
    ItemGroup = serializers.CharField(max_length=200)
    ItemSubGroup = serializers.CharField(max_length=200)
    Cluster = serializers.CharField(max_length=200)
    SubCluster = serializers.CharField(max_length=200)
    SheetNo = serializers.IntegerField()

