from dataclasses import field
from ..models import *
from rest_framework import serializers


class M_ItemsSerializer01(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = '__all__'


class M_ItemsSerializer02(serializers.Serializer):
    id = serializers.IntegerField()
    ItemGroup_id = serializers.IntegerField()
    ItemGroupName = serializers.CharField()
    Name = serializers.CharField(max_length=500)
    Sequence = serializers.DecimalField(max_digits=5, decimal_places=2)
    BaseUnitID_id = serializers.IntegerField()
    GSTPercentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    MRP = serializers.DecimalField(max_digits=20, decimal_places=2)
    Rate = serializers.DecimalField(max_digits=20, decimal_places=2)
    isActive = serializers.BooleanField(default=False)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField()


class ItemMarginSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemMargin
        fields = ['PriceList', 'Margin']

class ItemGMHSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemGMH
        fields = ['GSTPercentage', 'MRP', 'HSNCode']
        
        
class ItemDivisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemDivisions
        fields = ['Division']          
        
class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemImages
        fields = ['ImageType', 'Item_pic']        
         
# class ItemUnitsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MC_ItemUnits
#         fields = ['UnitID', 'BaseUnitQuantity' ]
        
class ItemCategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['CategoryType', 'Category', 'SubCategory']


class ItemSerializer(serializers.ModelSerializer):
    
    ItemCategoryDetails = ItemCategoryDetailsSerializer(many=True)
    
    # ItemUnitDetails = ItemUnitsSerializer(many=True)
    
    ItemImagesdetails = ItemImagesSerializer(many=True)
    
    ItemDivisiondetails = ItemDivisionsSerializer(many=True) 
    
    ItemGstDetails = ItemGMHSerializer(many=True)

    ItemMarginDetails = ItemMarginSerializer(many=True)
    
    

    class Meta:
        model = M_Items
        fields = ['Name', 'ShortName', 'Sequence', 'Company', 'BaseUnitID', 'BarCode', 'isActive',
                  'CreatedBy', 'UpdatedBy','ItemCategoryDetails', 'ItemUnitDetails', 'ItemImagedetails', 'ItemDivisiondetails', 'ItemGstDetails' ,'ItemMarginDetails']

    def create(self, validated_data):
        ItemCategorys_data = validated_data.pop('ItemCategoryDetails')
        ItemUnits_data = validated_data.pop('ItemUnitDetails')
        ItemImages_data = validated_data.pop('ItemImagedetails')
        ItemDivisions_data = validated_data.pop('ItemDivisiondetails')
        ItemGsts_data = validated_data.pop('ItemGstDetails')
        ItemMargins_data = validated_data.pop('ItemMarginDetails')
        ItemID= M_Items.objects.create(**validated_data)
        
        for ItemCategory_data in ItemCategorys_data:
            ItemCategorys = MC_ItemCategoryDetails.objects.create(Item=ItemID, **ItemCategory_data)

        # for ItemUnit_data in ItemUnits_data:
        #     ItemUnits = MC_ItemUnits.objects.create(Item=ItemID, **ItemUnit_data)
            
        for ItemImage_data in ItemImages_data:
            ItemImage = MC_ItemImages.objects.create(Item=ItemID, **ItemImage_data)
        
        for ItemDivision_data in ItemDivisions_data:
            ItemDivision = MC_ItemDivisions.objects.create(Item=ItemID, **ItemDivision_data)    
        
        for ItemGst_data in ItemGsts_data:
            ItemGstMrp = MC_ItemGMH.objects.create(Item=ItemID, **ItemGst_data)
        
        for ItemMargin_data in ItemMargins_data:
            ItemMargin = MC_ItemMargin.objects.create(Item=ItemID, **ItemMargin_data)             

        return ItemID
