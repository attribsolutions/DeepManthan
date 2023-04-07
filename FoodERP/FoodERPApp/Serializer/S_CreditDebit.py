from rest_framework import serializers
from ..models import *



# Credit Or Debit Save Serializer 
class CreditDebitNoteSerializer(serializers.ModelSerializer):
    
    class Meta :
        model= T_CreditDebitNotes
        fields = '__all__'
        
        