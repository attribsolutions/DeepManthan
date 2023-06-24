
from rest_framework import serializers

from ..Serializer.S_GSTHSNCode import M_GstHsnCodeSerializer

from ..Serializer.S_Mrps import M_MRPsSerializer
from ..Serializer.S_Orders import Mc_ItemUnitSerializerThird

from ..Serializer.S_Items import M_ItemsSerializer01
from ..models import *

class InvoicegovUploadSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    userGstin=serializers.CharField(max_length=500)
    supply_type = serializers.CharField(max_length=500)
    document_type=serializers.CharField(max_length=500)
    document_number = serializers.CharField(max_length=500)
    document_date = serializers.CharField(max_length=500)
    Seller_gstin = serializers.CharField(max_length=500)
    seller_legal_name = serializers.CharField(max_length=500)
    seller_address1 =  serializers.CharField(max_length=500)
    Seller_location =serializers.CharField(max_length=500)
    seller_pincode = serializers.BooleanField(default=False)
    Seller_state_code =  serializers.CharField(max_length=500)
    
    Buyer_gstin = serializers.CharField(max_length=500)
    Buyer_legal_name =  serializers.CharField(max_length=500)
    Buyer_address1 = serializers.CharField(max_length=500)
    Buyer_location = serializers.CharField(max_length=500)
    buyer_pincode = serializers.CharField(max_length=500)
    place_of_supply = serializers.CharField(max_length=500)
    Buyer_state_code = serializers.CharField(max_length=500)
    Start_Invoice_Date = serializers.CharField(max_length=500)
    End_Invoice_Date = serializers.CharField(max_length=500)
    total_assessable_value = serializers.CharField(max_length=500)
    total_invoice_value = serializers.CharField(max_length=500)
    total_cgst_value = serializers.CharField(max_length=500)
    total_sgst_value = serializers.CharField(max_length=500)
    total_igst_value = serializers.CharField(max_length=500)
    transportation_mode = serializers.CharField(max_length=500)
    # transportation_distance = serializers.CharField(max_length=500)


class InvoiceItemgovUploadSerializer(serializers.ModelSerializer):
    Item = M_ItemsSerializer01(read_only=True)
    MRP = M_MRPsSerializer(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta:
        model = TC_InvoiceItems
        fields = '__all__'
    
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_States
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Districts
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Cities
        fields = '__all__'   

class VehiclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Vehicles
        fields = '__all__'                

class MC_PartyAdressSerializer(serializers.ModelSerializer):
    Address = serializers.CharField() 
    class Meta:
        model = MC_PartyAddress
        fields = '__all__'

class PartiesSerializerSecond(serializers.ModelSerializer):
    PartyAddress=MC_PartyAdressSerializer(many=True)
    State = StateSerializer(read_only=True)
    District = DistrictSerializer(read_only=True)
    City = CitySerializer(read_only=True)
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email','PartyAddress','State','District','City']


class InvoicegovUploadSerializer(serializers.ModelSerializer):
        InvoiceItems=InvoiceItemgovUploadSerializer(many=True)
        Customer = PartiesSerializerSecond(read_only=True)
        Party = PartiesSerializerSecond(read_only=True)
        Vehicle =VehiclesSerializer(read_only=True)
        class Meta:
            model = T_Invoices
            fields = '__all__'