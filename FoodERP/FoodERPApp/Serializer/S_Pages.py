from operator import truediv
from black import maybe_install_uvloop
from rest_framework import serializers

from ..models import *


class ControlTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ControlTypeMaster
        fields = ['id','Name']

class FieldValidationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_FieldValidations
        fields = ['id','Name','RegularExpression']        


class MC_PagePageAccessSerializer(serializers.Serializer):
   
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)

class MC_PageFieldMasterSerializerSecond(serializers.Serializer):
       
    id = serializers.IntegerField()
    ControlID = serializers.IntegerField()
    ControlType_id = serializers.IntegerField()
    CName = serializers.CharField(max_length=100)
    FieldLabel = serializers.CharField(max_length=300)
    IsCompulsory = serializers.BooleanField(default=False)
    DefaultSort =  serializers.BooleanField(default=False)    
    FieldValidation_id = serializers.IntegerField()
    FName = serializers.CharField(max_length=100)         
    ListPageSeq = serializers.IntegerField()
    ShowInListPage = serializers.BooleanField(default=False) 
    ShowInDownload = serializers.BooleanField(default=False)
    DownloadDefaultSelect = serializers.BooleanField(default=False) 

        

class M_PagesSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    PageHeading=serializers.CharField(max_length=500)
    PageDescription = serializers.CharField(max_length=500)
    PageDescriptionDetails = serializers.CharField(max_length=500)
    ModuleID = serializers.IntegerField(read_only=True)
    ModuleName=serializers.CharField(max_length=100)
    isActive = serializers.BooleanField(default=False)
    DisplayIndex = serializers.IntegerField()
    Icon = serializers.CharField(max_length=100)
    ActualPagePath = serializers.CharField(max_length=100)
    PageType = serializers.IntegerField()
    RelatedPageID = serializers.IntegerField()
    RelatedPageName=serializers.CharField(max_length=100)
    IsDivisionRequired = serializers.BooleanField(default=False)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField() 
    
class M_PagesSerializer2(serializers.ModelSerializer):
    class Meta:
        model = M_Pages
        fields ="__all__" 

class MC_PageFieldMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_PageFieldMaster
        fields = ['ControlType','FieldLabel','IsCompulsory','FieldValidation','ListPageSeq','ShowInListPage','ShowInDownload','DownloadDefaultSelect']         

class MC_PagePageAccessSerializer1(serializers.ModelSerializer):
    class Meta:
        model = MC_PagePageAccess
        fields =['Access']
        
class M_PagesSerializer1(serializers.ModelSerializer):
    class Meta:
        model = M_Pages
        fields ="__all__"   
   
    PagePageAccess=MC_PagePageAccessSerializer1(many=True)
    PageFieldMaster=MC_PageFieldMasterSerializer(many=True)
    def create(self, validated_data):
        PageAccess_data = validated_data.pop('PagePageAccess')
        PageFieldMaster = validated_data.pop('PageFieldMaster')
       
        Pages = M_Pages.objects.create(**validated_data)
        
        for data in PageAccess_data:
            MC_PagePageAccess.objects.create(Page=Pages, **data)
            
        for PageFielddata in  PageFieldMaster:
            MC_PageFieldMaster.objects.create(Page=Pages,**PageFielddata) 
              
        return Pages

    def update(self, instance, validated_data):
            
            # * Page Info
            instance.Name = validated_data.get(
                'Name', instance.Name)
            instance.PageHeading = validated_data.get(
                'PageHeading', instance.PageHeading)
            instance.PageDescription = validated_data.get(
                'PageDescription', instance.PageDescription)
            instance.PageDescriptionDetails = validated_data.get(
                'PageDescriptionDetails', instance.PageDescriptionDetails)
            instance.Module = validated_data.get(
                'Module', instance.Module)
            instance.isActive = validated_data.get(
                'isActive', instance.isActive)
            instance.DisplayIndex = validated_data.get(
                'DisplayIndex', instance.DisplayIndex)
            instance.Icon = validated_data.get(
                'Icon', instance.Icon)
            instance.ActualPagePath = validated_data.get(
                'ActualPagePath', instance.ActualPagePath)
            
            instance.PageType = validated_data.get(
                'PageType', instance.PageType)
            instance.RelatedPageID = validated_data.get(
                'RelatedPageID', instance.RelatedPageID)
            instance.IsDivisionRequired = validated_data.get(
                'IsDivisionRequired', instance.IsDivisionRequired)
            instance.save()

            for Access in instance.PagePageAccess.all():
                Access.delete()
                
            for PageField in instance.PageFieldMaster.all():
                PageField.delete()
                

            if (instance.PageType !=1):
                for PagePageAccess_data in validated_data['PagePageAccess']:
                    PageAccess = MC_PagePageAccess.objects.create(Page=instance, **PagePageAccess_data)
                instance.PagePageAccess.add(PageAccess)
                
                for PageField_data in validated_data['PageFieldMaster']:
                    PageField = MC_PageFieldMaster.objects.create(Page=instance, **PageField_data)
                instance.PageFieldMaster.add(PageField)
            
            return instance   
    

        

      