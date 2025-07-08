from ..models import *
from rest_framework import serializers

class SchemeSerializer(serializers.ModelSerializer):
    TotalVoucherCodeCount = serializers.SerializerMethodField()
    ActiveVoucherCodeCount = serializers.SerializerMethodField()
    InactiveVoucherCodeCount = serializers.SerializerMethodField()

    class Meta:
        model = M_Scheme
        fields = fields = ['id','SchemeName','SchemeValue','ValueIn','FromPeriod','ToPeriod','FreeItemID','VoucherLimit','QRPrefix',
                          'IsActive','BillAbove','SchemeDetails','Message','OverLappingScheme','SchemeValueUpto','Column1','Column2',
                          'Column3','ShortName','SchemeTypeID','TotalVoucherCodeCount','ActiveVoucherCodeCount','InactiveVoucherCodeCount']

    def get_TotalVoucherCodeCount(self, obj):
        return obj.GiftVoucherSchemeID.count()

    def get_ActiveVoucherCodeCount(self, obj):
        return obj.GiftVoucherSchemeID.filter(IsActive=True).count()

    def get_InactiveVoucherCodeCount(self, obj):
        return obj.GiftVoucherSchemeID.filter(IsActive=False).count()



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
    
    
class SchemeListSerializerSecond(serializers.Serializer):
    id = serializers.IntegerField()
    SchemeName = serializers.CharField(max_length=100)
    SchemeTypeID_id = serializers.IntegerField()
    SchemeValue = serializers.DecimalField(max_digits=20, decimal_places=3)
    ValueIn = serializers.CharField(max_length=100)
    FromPeriod = serializers.DateField()
    ToPeriod = serializers.DateField()
    FreeItemID = serializers.IntegerField()
    VoucherLimit = serializers.IntegerField()
    QRPrefix = serializers.CharField(max_length=100)
    IsActive = serializers.BooleanField()
    BillAbove = serializers.DecimalField(max_digits=20, decimal_places=3)
    SchemeDetails = serializers.CharField(max_length=100)
    Message = serializers.CharField(max_length=500) 
    OverLappingScheme = serializers.BooleanField()
    SchemeValueUpto = serializers.DecimalField(max_digits=20, decimal_places=3)
    Column1 = serializers.CharField(max_length=100)
    Column2 = serializers.CharField(max_length=100)
    Column3 = serializers.CharField(max_length=100)
    ShortName = serializers.CharField(max_length=500) 
    SchemeQuantity = serializers.DecimalField(max_digits=20, decimal_places=3)