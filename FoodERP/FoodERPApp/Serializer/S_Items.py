from  ..models import M_Items, M_ItemsGroup
from rest_framework import serializers


class M_ItemsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_ItemsGroup
        fields = ['ID','Name','Sequence']

class M_ItemsSerializer(serializers.ModelSerializer):
    ItemGroup=M_ItemsGroupSerializer()
    class Meta:
        model =  M_Items
        fields = '__all__'