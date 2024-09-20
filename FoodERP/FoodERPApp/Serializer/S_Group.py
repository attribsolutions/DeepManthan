from rest_framework import serializers
from ..models import *

# Post and Put Methods Serializer

class M_GroupSerializerForItem(serializers.ModelSerializer):
    class Meta:
        model = M_Group
        fields = '__all__'

# Get ALL Group,Get Single Group,Get Group On GroupType Methods Serializers

class GroupTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =  M_GroupType
        fields = '__all__'

class GroupSerializerSecond(serializers.ModelSerializer):
    GroupType = GroupTypeSerializerSecond(read_only=True)
    class Meta:
        model = M_Group
        fields = '__all__'      

class GroupSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Group
        fields = '__all__' 
        
        
class M_GroupData(serializers.Serializer): 
    id =  serializers.IntegerField() 
    GroupID =  serializers.IntegerField() 
    GroupName = serializers.CharField(max_length=500) 
    GroupSequence=serializers.DecimalField(max_digits=20, decimal_places=2)
    GroupType_id =  serializers.IntegerField() 
    # Item_id =  serializers.IntegerField() 
    SubGroup_id =  serializers.IntegerField() 
    ItemSequence = serializers.DecimalField(max_digits=20, decimal_places=2)
    SubGroupID =  serializers.IntegerField() 
    SubGroupName = serializers.CharField(max_length=500) 
    SubGroupSequence = serializers.DecimalField(max_digits=20, decimal_places=2) 
    ItemID =  serializers.IntegerField() 
    ItemName = serializers.CharField(max_length=500) 
    ItemSequence = serializers.DecimalField(max_digits=20, decimal_places=2)  