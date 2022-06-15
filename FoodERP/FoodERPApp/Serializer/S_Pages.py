from rest_framework import serializers
# from ..Serializer.S_Modules import *
# from ..Serializer.S_RoleAccess import DynamicFieldsModelSerializer

from ..models import *

class MC_PagePageAccessSerializer(serializers.Serializer):
    
    # class Meta:
    #     model = MC_PagePageAccess
    #     # fields ="__all__"
    #     fields = ['ID','PageID','AccessID']
    ID = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)

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
    class Meta:
        model = M_Pages
        fields ="__all__"
        # fields = ['ID','Name','Description','Module','isActive','DisplayIndex', 'Icon','ActualPagePath','isShowOnMenu','PageType','RelatedPageID','PagePageAccess']

class M_PagesSerializerForPost(serializers.ModelSerializer):
    class Meta:
        model = M_Pages
        fields ="__all__"
    def create(self, validated_data):
        PagePageAccess_data = validated_data.pop('PagePageAccess')
        Pages = M_Pages.objects.create(**validated_data)
        for PagePageAccess in PagePageAccess_data:
            MC_PagePageAccess.objects.create(PageID=Pages, **PagePageAccess )
        
        return Pages

        
    

        

      