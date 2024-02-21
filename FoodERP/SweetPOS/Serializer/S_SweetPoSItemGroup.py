from rest_framework import serializers
from FoodERPApp.models import *

class SubGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_SubGroup
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    Subgroups = SubGroupSerializer(many=True, read_only=True)
    
    class Meta:
        model = M_Group
        fields = '__all__'

