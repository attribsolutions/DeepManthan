from asyncore import read
from dataclasses import field
from ..models import *
from rest_framework import serializers


class M_ItemsSerializer01(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = '__all__'

class ItemsSerializerList(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    ShortName = serializers.CharField(max_length=500)
    BaseUnitName = serializers.CharField(max_length=500)
    CompanyName = serializers.CharField(max_length=500)
    BarCode = serializers.CharField(max_length=500)

class ImageTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ImageTypes
        fields = '__all__'

class ItemGSTHSNSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemGSTHSNCode
        fields = ['EffectiveDate', 'GSTPercentage', 'HSNCode', 'CreatedBy', 'UpdatedBy']
    
class ItemMarginSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_MarginMaster
        fields = ['EffectiveDate', 'Margin', 'IsDelete', 'CreatedBy', 'UpdatedBy', 'Company', 'PriceList', 'Party']

class ItemMRPSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_MRPMaster
        fields = ['EffectiveDate', 'MRP', 'CreatedBy','UpdatedBy','Company','Party', 'Division']
         
class ItemDivisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemDivisions
        fields = ['Division']          
        
class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemImages
        fields = ['ImageType', 'Item_pic']        
         
class ItemUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemUnits
        fields = ['UnitID', 'BaseUnitQuantity' ]
        
class ItemCategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['CategoryType', 'Category', 'SubCategory']


class ItemSerializer(serializers.ModelSerializer):
    
    ItemCategoryDetails = ItemCategoryDetailsSerializer(many=True)
    
    ItemUnitDetails = ItemUnitsSerializer(many=True)
    
    ItemImagesDetails = ItemImagesSerializer(many=True)
    
    ItemDivisionDetails = ItemDivisionsSerializer(many=True) 
    
    ItemMRPDetails = ItemMRPSerializer(many=True)

    ItemMarginDetails = ItemMarginSerializer(many=True)
    
    ItemGSTHSNDetails = ItemGSTHSNSerializer(many=True)
    
   
    class Meta:
        model = M_Items
        fields = ['Name', 'ShortName', 'Sequence', 'Company', 'BaseUnitID', 'BarCode', 'isActive','LinkedItem','CreatedBy', 'UpdatedBy','ItemCategoryDetails', 'ItemUnitDetails', 'ItemImagesDetails', 'ItemDivisionDetails', 'ItemMRPDetails', 'ItemMarginDetails', 'ItemGSTHSNDetails' ]
       
    def create(self, validated_data):
        ItemCategorys_data = validated_data.pop('ItemCategoryDetails')
        ItemUnits_data = validated_data.pop('ItemUnitDetails')
        ItemImages_data = validated_data.pop('ItemImagesDetails')
        ItemDivisions_data = validated_data.pop('ItemDivisionDetails')
        ItemMRPs_data = validated_data.pop('ItemMRPDetails')
        ItemMargins_data = validated_data.pop('ItemMarginDetails')
        ItemGSTHSNs_data = validated_data.pop('ItemGSTHSNDetails')
        ItemID= M_Items.objects.create(**validated_data)
        
        for ItemCategory_data in ItemCategorys_data:
            ItemCategorys = MC_ItemCategoryDetails.objects.create(Item=ItemID, **ItemCategory_data)

        for ItemUnit_data in ItemUnits_data:
            ItemUnits = MC_ItemUnits.objects.create(Item=ItemID, **ItemUnit_data)
            
        for ItemImage_data in ItemImages_data:
            ItemImage = MC_ItemImages.objects.create(Item=ItemID, **ItemImage_data)
        
        for ItemDivision_data in ItemDivisions_data:
            ItemDivision = MC_ItemDivisions.objects.create(Item=ItemID, **ItemDivision_data)    
        
        for ItemMRP_data in ItemMRPs_data:
            ItemMrp = M_MRPMaster.objects.create(Item=ItemID, **ItemMRP_data)
        
        for ItemMargin_data in ItemMargins_data:
            ItemMargin = M_MarginMaster.objects.create(Item=ItemID, **ItemMargin_data)
        
        for ItemGSTHSN_data in ItemGSTHSNs_data:
            ItemGSTHSN = MC_ItemGSTHSNCode.objects.create(Item=ItemID, **ItemGSTHSN_data)                  

        return ItemID
    
    def update(self, instance, validated_data):

        instance.Name = validated_data.get(
            'Name', instance.Name)
        instance.ShortName = validated_data.get(
            'ShortName', instance.ShortName)
        instance.Sequence = validated_data.get(
            'Sequence', instance.Sequence)
        instance.Company = validated_data.get(
            'Company', instance.Company)
        instance.BaseUnitID = validated_data.get(
            'BaseUnitID', instance.BaseUnitID)
        instance.BarCode = validated_data.get(
            'BarCode', instance.BarCode)
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)    
        instance.save()
        
        for a in instance.ItemCategoryDetails.all():
            a.delete()
        for b in instance.ItemUnitDetails.all():
            b.delete()
        for c in instance.ItemImagesDetails.all():
            c.delete()
        for d in instance.ItemDivisionDetails.all():
            d.delete()
        for e in instance.ItemMRPDetails.all():
            e.delete()  
        for f in instance.ItemMarginDetails.all():
            f.delete()                    
        for g in instance.ItemGSTHSNDetails.all():
            g.delete()
        
        for ItemCategory_data in  validated_data['ItemCategoryDetails']:
            ItemCategorys = MC_ItemCategoryDetails.objects.create(Item=instance, **ItemCategory_data)

        for ItemUnit_data in validated_data['ItemUnitDetails']:
            ItemUnits = MC_ItemUnits.objects.create(Item=instance, **ItemUnit_data)
            
        for ItemImage_data in validated_data['ItemImagesDetails']:
            ItemImage = MC_ItemImages.objects.create(Item=instance, **ItemImage_data)
        
        for ItemDivision_data in validated_data['ItemDivisionDetails']:
            ItemDivision = MC_ItemDivisions.objects.create(Item=instance, **ItemDivision_data)    
        
        for ItemMRP_data in validated_data['ItemMRPDetails']:
            ItemGstMrp = M_MRPMaster.objects.create(Item=instance, **ItemMRP_data)
        
        for ItemMargin_data in validated_data['ItemMarginDetails']:
            ItemMargin = M_MarginMaster.objects.create(Item=instance, **ItemMargin_data)
        
        for ItemGSTHSN_data in validated_data['ItemGSTHSNDetails']:
            ItemGSTHSN = MC_ItemGSTHSNCode.objects.create(Item=instance, **ItemMargin_data)    
        
        return instance 
         

class UnitSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class ItemGSTHSNSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemGSTHSNCode
        fields = ['EffectiveDate', 'GSTPercentage', 'HSNCode', 'CreatedBy', 'UpdatedBy']

class CompanySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = ['id','Name'] 
        
class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name'] 
                      
class ItemMarginSerializerSecond(serializers.ModelSerializer):
    Company = CompanySerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    
    class Meta:
        model = M_MarginMaster
        fields = ['EffectiveDate', 'Margin', 'CreatedBy', 'UpdatedBy', 'Company', 'PriceList', 'Party']

class ItemMRPSerializerSecond(serializers.ModelSerializer):
    Company = CompanySerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    Division = PartiesSerializerSecond(read_only=True)
    class Meta:
        model = M_MRPMaster
        fields = ['EffectiveDate', 'MRP', 'CreatedBy','UpdatedBy','Company','Party', 'Division']        
              
class ItemDivisionsSerializerSecond(serializers.ModelSerializer):
    Division = PartiesSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemDivisions
        fields = ['id','Division']
                   
class ImageTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ImageTypes
        fields = ['id','Name']
        
class ItemImagesSerializerSecond(serializers.ModelSerializer):
    ImageType = ImageTypesSerializer(read_only=True)
    class Meta:
        model = MC_ItemImages
        fields = ['id','Item_pic', 'ImageType']
         
class ItemUnitsSerializerSecond(serializers.ModelSerializer):
    UnitID = UnitSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID', 'BaseUnitQuantity' ]
        
class ItemSubCategorySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_ProductSubCategory
        fields = ['id','Name']

class ItemCategorySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_ProductCategory
        fields = ['id','Name']
        
class ItemCategoryTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_ProductCategoryType
        fields = ['id','Name']

class ItemCategoryDetailsSerializerSecond(serializers.ModelSerializer):
    SubCategory = ItemSubCategorySerializerSecond(read_only=True)
    Category = ItemCategorySerializerSecond(read_only=True)
    CategoryType = ItemCategoryTypeSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['id','Category','CategoryType','SubCategory']

class ItemSerializerSecond(serializers.ModelSerializer):
    Company=CompanySerializerSecond()
    BaseUnitID = UnitSerializerSecond()
    ItemCategoryDetails = ItemCategoryDetailsSerializerSecond(read_only=True,many=True)
    ItemUnitDetails =ItemUnitsSerializerSecond(many=True)
    ItemImagesDetails = ItemImagesSerializerSecond(read_only=True,many=True)
    ItemDivisionDetails = ItemDivisionsSerializerSecond(many=True)
    ItemMRPDetails = ItemMRPSerializerSecond(many=True)
    ItemMarginDetails = ItemMarginSerializerSecond(many=True)
    ItemGSTHSNDetails = ItemGSTHSNSerializerSecond(many=True)
    
    class Meta:
        model = M_Items
        fields='__all__'
    
    
   
    



