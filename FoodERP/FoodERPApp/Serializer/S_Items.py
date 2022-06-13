from  ..models import M_Items
from rest_framework import serializers


class M_ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_Items
        fields = '__all__'