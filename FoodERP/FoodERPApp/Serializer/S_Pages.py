from rest_framework import serializers
from ..Serializer.S_Modules import *
from ..Serializer.S_RoleAccess import DynamicFieldsModelSerializer

from ..models import *

class M_PagesSerializer(DynamicFieldsModelSerializer):
    Module = H_ModulesSerializer()
    # SubModule = H_SubModulesSerializer()
    class Meta:
        model = M_Pages 
        fields ="__all__"

class M_PagesSerializer1(serializers.ModelSerializer):
    # Module = H_ModulesSerializer()
    # SubModule = SubModuleListSerializer()
    class Meta:
        model = M_Pages
        # fields = ['ID','Name','Description','Module','Submodule','isActive','DisplayIndex','Icon','ActualPagePath']    
        fields ="__all__"