from rest_framework import serializers
from ..Serializer.S_Modules import *
from ..Serializer.S_RoleAccess import DynamicFieldsModelSerializer

from ..models import *

class MC_PagePageAccessSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MC_PagePageAccess
        fields ="__all__"

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
    # Module = H_ModulesSerializer()
    # SubModule = SubModuleListSerializer()
    class Meta:
        model = M_Pages
        # fields = ['ID','Name','Description','Module','Submodule','isActive','DisplayIndex','Icon','ActualPagePath']    
        fields ="__all__"

      