from ..Views.V_CommFunction import *
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

class ItemShelfLifeSerializer(serializers.ModelSerializer):
     class Meta:
        model = MC_ItemShelfLife
        fields = ['Days', 'CreatedBy', 'UpdatedBy']

class ItemGSTHSNSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_GSTHSNCode
        fields = ['EffectiveDate', 'GSTPercentage', 'HSNCode', 'CreatedBy','Company', 'UpdatedBy','CommonID']
    
class ItemMarginSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_MarginMaster
        fields = ['EffectiveDate', 'Margin', 'CreatedBy', 'UpdatedBy', 'Company', 'PriceList', 'Party','CommonID']

class ItemMRPSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_MRPMaster
        fields = ['EffectiveDate', 'MRP', 'CreatedBy','UpdatedBy','Company','Party', 'Division','CommonID']
         
class ItemDivisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PartyItems
        fields = ['Party']          
        
class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemImages
        fields = ['ImageType', 'Item_pic']        
         
class ItemUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemUnits
        fields = ['UnitID', 'BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion']
        
               
class ItemGroupDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemGroupDetails
        fields = ['GroupType', 'Group', 'SubGroup']        
        
class ItemCategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['CategoryType', 'Category']


class ItemSerializer(serializers.ModelSerializer):
    
    ItemCategoryDetails = ItemCategoryDetailsSerializer(many=True)
     
    ItemGroupDetails = ItemGroupDetailsSerializer(many=True)
    
    ItemUnitDetails = ItemUnitsSerializer(many=True)
    
    ItemImagesDetails = ItemImagesSerializer(many=True)
    
    ItemDivisionDetails = ItemDivisionsSerializer(many=True) 
    
    ItemMRPDetails = ItemMRPSerializer(many=True)

    ItemMarginDetails = ItemMarginSerializer(many=True)
    
    ItemGSTHSNDetails = ItemGSTHSNSerializer(many=True)
    
    ItemShelfLife = ItemShelfLifeSerializer(many=True)
   
    class Meta:
        model = M_Items
        fields = ['Name', 'ShortName', 'Sequence', 'Company', 'BaseUnitID', 'BarCode','SAPItemCode', 'isActive', 'IsSCM', 'CanBeSold', 'CanBePurchase', 'BrandName', 'Tag','Length','Breadth','Height','StoringCondition','Grammage','CreatedBy', 'UpdatedBy','ItemCategoryDetails','ItemGroupDetails', 'ItemUnitDetails', 'ItemImagesDetails', 'ItemDivisionDetails', 'ItemMRPDetails', 'ItemMarginDetails', 'ItemGSTHSNDetails', 'ItemShelfLife' ]
       
    def create(self, validated_data):
        ItemCategorys_data = validated_data.pop('ItemCategoryDetails')
        ItemGroups_data = validated_data.pop('ItemGroupDetails')
        ItemUnits_data = validated_data.pop('ItemUnitDetails')
        ItemImages_data = validated_data.pop('ItemImagesDetails')
        ItemDivisions_data = validated_data.pop('ItemDivisionDetails')
        ItemMRPs_data = validated_data.pop('ItemMRPDetails')
        ItemMargins_data = validated_data.pop('ItemMarginDetails')
        ItemGSTHSNs_data = validated_data.pop('ItemGSTHSNDetails')
        ItemShelfLifes_data = validated_data.pop('ItemShelfLife')
        ItemID= M_Items.objects.create(**validated_data)
        
        for ItemCategory_data in ItemCategorys_data:
            ItemCategorys = MC_ItemCategoryDetails.objects.create(Item=ItemID, **ItemCategory_data)
        
        for ItemGroup_data in ItemGroups_data:
            ItemGroups = MC_ItemGroupDetails.objects.create(Item=ItemID, **ItemGroup_data)    

        for ItemUnit_data in ItemUnits_data:
        
            ItemUnits = MC_ItemUnits.objects.create(Item=ItemID,**ItemUnit_data)
            
        if ItemImages_data != '':
            for ItemImage_data in ItemImages_data:
                ItemImage = MC_ItemImages.objects.create(Item=ItemID, **ItemImage_data)
        
        for ItemDivision_data in ItemDivisions_data:
            ItemDivision = MC_PartyItems.objects.create(Item=ItemID, **ItemDivision_data)    
        
        for ItemMRP_data in ItemMRPs_data:
            ItemMrp = M_MRPMaster.objects.create(Item=ItemID, **ItemMRP_data)
        
        for ItemMargin_data in ItemMargins_data:
            ItemMargin = M_MarginMaster.objects.create(Item=ItemID, **ItemMargin_data)
        
        for ItemGSTHSN_data in ItemGSTHSNs_data:
            ItemGSTHSN = M_GSTHSNCode.objects.create(Item=ItemID, **ItemGSTHSN_data)
        
        for ItemShelfLife_data in ItemShelfLifes_data:
            MItemShelfLife = MC_ItemShelfLife.objects.create(Item=ItemID, **ItemShelfLife_data)                      
            
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
        instance.SAPItemCode = validated_data.get(
            'SAPItemCode', instance.SAPItemCode)
        instance.isActive = validated_data.get(
            'isActive', instance.isActive)
        instance.IsSCM = validated_data.get(
            'IsSCM', instance.IsSCM)
        instance.CanBeSold = validated_data.get(
            'CanBeSold', instance.CanBeSold)
        instance.CanBePurchase = validated_data.get(
            'CanBePurchase', instance.CanBePurchase)
        instance.BrandName = validated_data.get(
            'BrandName', instance.BrandName)
        instance.Tag = validated_data.get(
            'Tag', instance.Tag)
        instance.Length = validated_data.get(
            'Length', instance.Length)
        instance.Breadth = validated_data.get(
            'Breadth', instance.Breadth)
        instance.Height = validated_data.get(
            'Height', instance.Height)
        instance.StoringCondition = validated_data.get(
            'StoringCondition', instance.StoringCondition)
        instance.Grammage = validated_data.get(
            'Grammage', instance.Grammage)
            
        instance.save()
        
        for a in instance.ItemCategoryDetails.all():
            a.delete()
        
        for b in instance.ItemGroupDetails.all():
            b.delete()
                
        for c in instance.ItemUnitDetails.all():
            # print(c.id)
            SetFlag=MC_ItemUnits.objects.filter(id=c.id).update(IsDeleted=1)
            
        if validated_data['ItemImagesDetails'] != '':    
            for d in instance.ItemImagesDetails.all():
                d.delete()
            
        for e in instance.ItemDivisionDetails.all():
            e.delete()
        
        for f in instance.ItemShelfLife.all():
            SetFlag=MC_ItemShelfLife.objects.filter(id=f.id).update(IsDeleted=1) 
            
        # for f in instance.ItemMRPDetails.all():
        #     f.delete()  
        # for g in instance.ItemMarginDetails.all():
        #     g.delete()  
                          
        # for h in instance.ItemGSTHSNDetails.all():
        #     h.delete()
        
        for ItemCategory_data in  validated_data['ItemCategoryDetails']:
            ItemCategorys = MC_ItemCategoryDetails.objects.create(Item=instance, **ItemCategory_data)
        
        for ItemGroup_data in  validated_data['ItemGroupDetails']:
            ItemCategorys = MC_ItemGroupDetails.objects.create(Item=instance, **ItemGroup_data)    

        for ItemUnit_data in validated_data['ItemUnitDetails']:
            ItemUnits = MC_ItemUnits.objects.create(Item=instance, **ItemUnit_data)
            
        if validated_data['ItemImagesDetails'] != '':
            for ItemImage_data in validated_data['ItemImagesDetails']:
                ItemImage = MC_ItemImages.objects.create(Item=instance, **ItemImage_data)
        
        for ItemDivision_data in validated_data['ItemDivisionDetails']:
            ItemDivision = MC_PartyItems.objects.create(Item=instance, **ItemDivision_data)    
        
        for ItemMRP_data in validated_data['ItemMRPDetails']:
            ItemGstMrp = M_MRPMaster.objects.create(Item=instance, **ItemMRP_data)
        
        for ItemMargin_data in validated_data['ItemMarginDetails']:
            ItemMargin = M_MarginMaster.objects.create(Item=instance, **ItemMargin_data)
        
        for ItemGSTHSN_data in validated_data['ItemGSTHSNDetails']:
            ItemGSTHSN = M_GSTHSNCode.objects.create(Item=instance, **ItemGSTHSN_data) 
        
        for ItemShelfLife_data in validated_data['ItemShelfLife']:
            MItemShelfLife = MC_ItemShelfLife.objects.create(Item=instance, **ItemShelfLife_data)       
        
        return instance 
         
class CompanySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = C_Companies
        fields = ['id','Name'] 

class UnitSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name','SAPUnit']
        
class ItemGSTHSNSerializerSecond(serializers.ModelSerializer):
    Company = CompanySerializerSecond(read_only=True)
    class Meta:
        model = M_GSTHSNCode
        fields = ['id','EffectiveDate', 'GSTPercentage', 'HSNCode','Company','IsDeleted', 'CreatedBy', 'UpdatedBy']

class ItemShelfLifeSerializerSecond(serializers.ModelSerializer):
     class Meta:
        model = MC_ItemShelfLife
        fields = ['id','Days', 'CreatedBy', 'UpdatedBy','IsDeleted']
                
class PriceListSerializerSecond(serializers.ModelSerializer):
     class Meta:
        model = M_PriceList
        fields = ['id','Name']
    


        
class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name'] 
                      
class ItemMarginSerializerSecond(serializers.ModelSerializer):
    Company = CompanySerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    PriceList  = PriceListSerializerSecond(read_only=True)
    class Meta:
        model = M_MarginMaster
        fields = ['id','EffectiveDate', 'Margin', 'CreatedBy', 'UpdatedBy', 'Company', 'PriceList', 'Party','IsDeleted']
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(ItemMarginSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
         
        if not ret.get("Party", None):
            ret["Party"] = {"id": None, "Name": None}    
        return ret     
        
class ItemDivisionsSerializerSecond(serializers.ModelSerializer):
    Party = PartiesSerializerSecond(read_only=True)
    class Meta:
        model = MC_PartyItems
        fields = ['id','Party']
        
class ItemMRPSerializerSecond(serializers.ModelSerializer):
    Company = CompanySerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
    Division = PartiesSerializerSecond(read_only=True)
    class Meta:
        model = M_MRPMaster
        fields = ['id','EffectiveDate', 'MRP', 'CreatedBy','UpdatedBy','Company','Party', 'Division','IsDeleted']        
    
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(ItemMRPSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Division", None):
            ret["Division"] = {"id": None, "Name": None}
            
        if not ret.get("Party", None):
            ret["Party"] = {"id": None, "Name": None}    
        return ret  
                 
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
        fields = ['id','UnitID', 'BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion']

class ItemSubGroupSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = MC_SubGroup
        fields = ['id','Name']

class ItemGroupSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Group
        fields = ['id','Name']
        
class ItemGroupTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_GroupType
        fields = ['id','Name']        
        

class ItemCategorySerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Category
        fields = ['id','Name']
        
class ItemCategoryTypeSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_CategoryType
        fields = ['id','Name']

class ItemGroupDetailsSerializerSecond(serializers.ModelSerializer):
    SubGroup = ItemSubGroupSerializerSecond(read_only=True)
    Group = ItemGroupSerializerSecond(read_only=True)
    GroupType = ItemGroupTypeSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['id','GroupType','Group','SubGroup']
        
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(ItemGroupDetailsSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("SubGroup", None):
            ret["SubGroup"] = {"id": None, "Name": None}  
        return ret

class ItemCategoryDetailsSerializerSecond(serializers.ModelSerializer):
   
    Category = ItemCategorySerializerSecond(read_only=True)
    CategoryType = ItemCategoryTypeSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['id','CategoryType','Category']

class ItemSerializerSecond(serializers.ModelSerializer):
    Company=CompanySerializerSecond()
    BaseUnitID = UnitSerializerSecond()
    ItemCategoryDetails = ItemCategoryDetailsSerializerSecond(read_only=True,many=True)
    ItemGroupDetails = ItemGroupDetailsSerializerSecond(read_only=True,many=True)
    ItemUnitDetails =ItemUnitsSerializerSecond(many=True)
    ItemImagesDetails = ItemImagesSerializerSecond(read_only=True,many=True)
    ItemDivisionDetails = ItemDivisionsSerializerSecond(many=True)
    ItemMRPDetails = ItemMRPSerializerSecond(many=True)
    ItemMarginDetails = ItemMarginSerializerSecond(many=True)
    ItemGSTHSNDetails = ItemGSTHSNSerializerSecond(many=True)
    ItemShelfLife = ItemShelfLifeSerializerSecond(many=True)
    
    class Meta:
        model = M_Items
        fields='__all__'
    
    
class ItemGSTHSNSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_GSTHSNCode
        fields = ['GSTPercentage','HSNCode']

class ItemMRPSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_MRPMaster
        fields = ['MRP']

class ItemShelfLifeSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemShelfLife
        fields = ['Days']

class ItemGroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Group
        fields = ['id','Name']

class ItemSubGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_SubGroup
        fields = ['id','Name']

class ItemGroupDetailsSerializerThird(serializers.ModelSerializer):
    Group = ItemGroupNameSerializer(read_only=True)
    SubGroup = ItemSubGroupSerializer(read_only=True)
    GroupType = ItemGroupTypeSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemGroupDetails
        fields = ['Group', 'SubGroup','GroupType']
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(ItemGroupDetailsSerializerThird, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("SubGroup", None):
            ret["SubGroup"] = {"id": None, "Name": None}
      
        return ret
         

class ItemReportSerializer(serializers.ModelSerializer):
    ItemGroupDetails = ItemGroupDetailsSerializerThird(many=True)
    Company=CompanySerializerSecond()
    BaseUnitID = UnitSerializerSecond()

    class Meta:
        model = M_Items
        fields = ['id','Name', 'ShortName', 'Sequence', 'Company', 'BaseUnitID', 'BarCode','SAPItemCode', 'isActive','IsSCM', 'CanBeSold', 'CanBePurchase', 'BrandName', 'Tag', 'Length', 'Breadth','Height','StoringCondition','Grammage','CreatedBy', 'UpdatedBy','ItemGroupDetails']




