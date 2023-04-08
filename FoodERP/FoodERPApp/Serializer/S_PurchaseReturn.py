from ..models import *
from rest_framework import serializers
from ..Serializer.S_BankMaster import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *


class PurchaseReturnSerializer(serializers.ModelSerializer):
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'