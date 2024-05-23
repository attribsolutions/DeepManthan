from ..models import *
from rest_framework import serializers
from FoodERPApp.models import *


class SPOSstockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = T_SPOSStock
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = ['id', 'Name']