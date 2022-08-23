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

class MC_ItemsImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemsImages
        fields = ['ImageType', 'Item_pic']



class MC_ItemUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemUnits
        fields = ['UnitID', 'BaseUnitQuantity', 'IsBase', 'IsDefault']


class MC_ItemsGMMHSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemsGMMH
        fields = ['GSTPercentage', 'MRP', 'Margin', 'HSNCode']
         

class ItemCategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['ProductCategory']


class ItemSerializer(serializers.ModelSerializer):
    
    ItemCategoryDetails = ItemCategoryDetailsSerializer(many=True)

    ItemGstDetails = MC_ItemsGMMHSerializer(many=True)

    ItemUnitDetails = MC_ItemUnitsSerializer(many=True)
    
    # ItemImagesdetails = MC_ItemsImagesSerializer(many=True) ,'ItemImagesdetails'
    

    class Meta:
        model = M_Items
        fields = ['Name', 'ShortName', 'Sequence', 'Company', 'BaseUnitID', 'BarCode', 'isActive',
                  'CreatedBy', 'UpdatedBy','ItemCategoryDetails', 'ItemGstDetails', 'ItemUnitDetails']

    def create(self, validated_data):
        ItemCategorys_data = validated_data.pop('ItemCategoryDetails')
        ItemGsts_data = validated_data.pop('ItemGstDetails')
        ItemUnits_data = validated_data.pop('ItemUnitDetails')
        # ItemImages_data = validated_data.pop('ItemImagedetails')
        
        ItemID= M_Items.objects.create(**validated_data)
        for ItemCategory_data in ItemCategorys_data:
            ItemCategorys = MC_ItemCategoryDetails.objects.create(Item=ItemID, **ItemCategory_data)

        for ItemGst_data in ItemGsts_data:
            ItemGstMrpMargin = MC_ItemsGMMH.objects.create(
                Item=ItemID, **ItemGst_data)

        for ItemUnit_data in ItemUnits_data:
            ItemUnits = MC_ItemUnits.objects.create(
                Item=ItemID, **ItemUnit_data)
                
        # for ItemImage_data in ItemImages_data:
        #     ItemImage = MC_ItemsGMMH.objects.create(
        #         Item=ItemID, **ItemImage_data)     

        return ItemID
