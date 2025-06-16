from ..models import *
from rest_framework import serializers

class SchemeSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_Scheme
        fields = '__all__'

class SchemeSerializer1(serializers.ModelSerializer):
    class Meta :
        model= M_Scheme
        fields = ['id','SchemeName']      
        
class SchemeTypeSerializer(serializers.ModelSerializer):
    class Meta :
        model= M_SchemeType
        fields = '__all__'
        
class SchemeItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model=MC_SchemeItems
        fields='__all__'
        extra_kwargs = {
            'SchemeID': {'read_only': True}
        }
        
class SchemePartiesSerializer(serializers.ModelSerializer):
    class Meta:
        model=MC_SchemeParties
        fields = '__all__'
        extra_kwargs = {
            'SchemeID': {'read_only': True}
            
        }
class SchemeDetailsSerializer(serializers.ModelSerializer):
    ItemDetails = SchemeItemsSerializer(many=True)
    PartyDetails = SchemePartiesSerializer(many=True)
    
    class Meta:
        model =  M_Scheme
        fields = [
            "id","SchemeName","SchemeValue","ValueIn","FromPeriod","ToPeriod","FreeItemID","VoucherLimit","QRPrefix",
            "IsActive","SchemeTypeID","BillAbove","Message","OverLappingScheme","SchemeDetails","SchemeValueUpto",
            "Column1","Column2","Column3", "ItemDetails", "PartyDetails", ]
    def create(self, validated_data):
        items   = validated_data.pop("ItemDetails", [])
        parties = validated_data.pop("PartyDetails", [])

        
        scheme = M_Scheme.objects.create(**validated_data)

       
        scheme_items = []
        for item in items:
            scheme_items.append(
                MC_SchemeItems(
                    SchemeID=scheme,           
                    Item=item["Item"],      
                    TypeForItem=item.get("TypeForItem", None),
                    DiscountType=item.get("DiscountType", None),
                    DiscountValue=item.get("DiscountValue", None),
                    Quantity=item.get("Quantity", None)
                )
            )
        MC_SchemeItems.objects.bulk_create(scheme_items)
        # Create MC_SchemeParties records linked to scheme
        scheme_parties = []
        for party in parties:            
            scheme_parties.append(
                MC_SchemeParties(
                    
                    SchemeID=scheme,
                    PartyID=party["PartyID"]
                )
            )
        MC_SchemeParties.objects.bulk_create(scheme_parties)

        return scheme