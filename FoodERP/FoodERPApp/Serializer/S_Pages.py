from operator import truediv
from black import maybe_install_uvloop
from rest_framework import serializers

from ..models import M_Pages, MC_PagePageAccess

class MC_PagePageAccessSerializer(serializers.Serializer):
   
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)

class M_PagesSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    Description = serializers.CharField(max_length=100)
    ModuleID = serializers.IntegerField(read_only=True)
    ModuleName=serializers.CharField(max_length=100)
    isActive = serializers.BooleanField(default=False)
    DisplayIndex = serializers.IntegerField()
    Icon = serializers.CharField(max_length=100)
    ActualPagePath = serializers.CharField(max_length=100)
    isShowOnMenu = serializers.BooleanField(default=False)
    PageType = serializers.IntegerField()
    RelatedPageID = serializers.IntegerField()
    RelatedPageName=serializers.CharField(max_length=100)
    CreatedBy = serializers.IntegerField(default=False)
    CreatedOn = serializers.DateTimeField()
    UpdatedBy = serializers.IntegerField(default=False)
    UpdatedOn = serializers.DateTimeField() 
    
class MC_PagePageAccessSerializer1(serializers.ModelSerializer):
    class Meta:
        model = MC_PagePageAccess
        fields =['Access']
class M_PagesSerializer1(serializers.ModelSerializer):
    class Meta:
        model = M_Pages
        fields ="__all__"   
   
    PagePageAccess=MC_PagePageAccessSerializer1(many=True)
    def create(self, validated_data):
        PageAccess_data = validated_data.pop('PagePageAccess')
       
        Pages = M_Pages.objects.create(**validated_data)
        for data in PageAccess_data:
            MC_PagePageAccess.objects.create(
                Page=Pages, 
                **data)
        return Pages

    def update(self, instance, validated_data):
            
            # * Page Info
            instance.Name = validated_data.get(
                'Name', instance.Name)
            instance.Description = validated_data.get(
                'Description', instance.Description)
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
            instance.isShowOnMenu = validated_data.get(
                'isShowOnMenu', instance.isShowOnMenu)
            instance.PageType = validated_data.get(
                'PageType', instance.PageType)
            instance.RelatedPageID = validated_data.get(
                'RelatedPageID', instance.RelatedPageID)
            instance.save()

            for Access in instance.PagePageAccess.all():
                Access.delete()

            for PagePageAccess_data in validated_data['PagePageAccess']:
                PageAccess = MC_PagePageAccess.objects.create(Page=instance, **PagePageAccess_data)
            instance.PagePageAccess.add(PageAccess)
            
            return instance   
    

        

      