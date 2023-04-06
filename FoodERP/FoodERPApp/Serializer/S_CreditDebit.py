from rest_framework import serializers
from ..models import *


class CreditNoteSerializer(serializers.ModelSerializer):
    
    class Meta :
        model= T_CreditNotes
        fields = '__all__'
        