from rest_framework import serializers
# from ..Serializer.S_Modules import *
# from ..Serializer.S_RoleAccess import DynamicFieldsModelSerializer

from ..models import *

class MC_PagePageAccessSerializer(serializers.Serializer):
    
    # class Meta:
    #     model = MC_PagePageAccess
    #     # fields ="__all__"
    #     fields = ['ID','PageID','AccessID']
    AccessID = serializers.IntegerField()
    AccessName = serializers.CharField(max_length=100)

class M_PagesSerializer(serializers.Serializer):
    
    ID = serializers.IntegerField()
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
    

class M_PagesSerializer1(serializers.ModelSerializer):
    
    PagePageAccess=MC_PagePageAccessSerializer(many=True)
    class Meta:
        model = M_Pages
        # fields ="__all__"
        fields = ['id','Name','Description','Module','isActive','DisplayIndex', 'Icon','ActualPagePath','isShowOnMenu','PageType','RelatedPageID','PagePageAccess']

    # def create(self, validated_data):
    #     PagePageAccess_data = validated_data.pop('PagePageAccess')
    #     Pages = M_Pages.objects.create(**validated_data)
    #     for PagePageAccess in PagePageAccess_data:
    #         MC_PagePageAccess.objects.create(PageID=Pages, **PagePageAccess )
        
    #     return Pages

        
    

        # def update(self, instance, validated_data):
            
        #     # * Page Info
        #     instance.Name = validated_data.get(
        #         'Name', instance.Name)
        #     instance.Description = validated_data.get(
        #         'Description', instance.Description)
        #     instance.Module = validated_data.get(
        #         'Module', instance.Module)
        #     instance.isActive = validated_data.get(
        #         'isActive', instance.isActive)
        #     instance.DisplayIndex = validated_data.get(
        #         'DisplayIndex', instance.DisplayIndex)
        #     instance.Icon = validated_data.get(
        #         'Icon', instance.Icon)
        #     instance.ActualPagePath = validated_data.get(
        #         'ActualPagePath', instance.ActualPagePath)
        #     instance.isShowOnMenu = validated_data.get(
        #         'isShowOnMenu', instance.isShowOnMenu)
        #     instance.PageType = validated_data.get(
        #         'PageType', instance.PageType)
        #     instance.RelatedPageID = validated_data.get(
        #         'RelatedPageID', instance.RelatedPageID)
            

        #     instance.save()

        #     for Access in instance.PagePageAccess.all():
        #         Access.delete()

            

        #     for PagePageAccess_data in validated_data['PagePageAccess']:
        #         PageAccess = PagePageAccess.objects.create(PageID=instance, **PagePageAccess_data)
        #     instance.PagePageAccess.add(PageAccess)
    
        

        #     return instance 

      