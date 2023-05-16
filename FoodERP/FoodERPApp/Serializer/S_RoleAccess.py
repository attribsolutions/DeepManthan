from rest_framework import serializers
from ..Serializer.S_Pages import *
from ..Serializer.S_Modules import *
from ..models import *

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name) 

class M_RoleAccessSerializer1(DynamicFieldsModelSerializer):
    
    class Meta:
        model = M_RoleAccess
        fields = '__all__'
        
        
class M_RoleAccessSerializerfordistinctModule(serializers.ModelSerializer):
    
    # Modules_id=H_ModulesSerializer2()
    class Meta:
        model = M_RoleAccess
        fields =['Modules_id']

class M_RoleAccessSerializerforRole(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

class M_PagesSerializerforRoleAccess(DynamicFieldsModelSerializer):
    
    class Meta:
        model = M_Pages
        fields ="__all__" 

class MC_RolePageAccessSerilaizer(serializers.ModelSerializer):

    class Meta:
        model = MC_RolePageAccess
        fields = ['PageAccess']
        
        
        
class M_PagesSerializerforRoleAccessNEW(serializers.Serializer):
    
    id = serializers.IntegerField()
    RelatedPageID=serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    PageHeading=serializers.CharField(max_length=500)
    PageDescription = serializers.CharField(max_length=500)
    PageDescriptionDetails = serializers.CharField(max_length=500)
    ActualPagePath = serializers.CharField(max_length=500)
    DisplayIndex = serializers.IntegerField()
    Icon =  serializers.CharField(max_length=500)
    isActive =  serializers.IntegerField()
    isShowOnMenu = serializers.BooleanField(default=False)
    Module_id =  serializers.IntegerField()
    PageType = serializers.IntegerField()
    RelatedPageID =  serializers.IntegerField()
    Pages_id = serializers.IntegerField()
    
    
class MC_RolePageAccessSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)    
  

    
class M_RoleAccessSerializer(serializers.ModelSerializer):
    RolePageAccess=MC_RolePageAccessSerilaizer(many=True)
    
    class Meta:
        model = M_RoleAccess
        fields = ['Role','Company','Division','Modules','Pages','RolePageAccess','CreatedBy','UpdatedBy']
         
    def create(self, validated_data):
        
        RolePageAccess_datas = validated_data.pop('RolePageAccess')
        RoleAccessID = M_RoleAccess.objects.create(**validated_data)
        for RolePageAccess_data in RolePageAccess_datas:
           MC_RolePageAccess.objects.create(RoleAccess=RoleAccessID, **RolePageAccess_data)
            
        return RoleAccessID
     

        
class M_RoleAccessSerializerGETList(serializers.Serializer):

    Role_id = serializers.IntegerField()
    RoleName = serializers.CharField(max_length=500)
    Division_id = serializers.IntegerField()
    DivisionName = serializers.CharField(max_length=500)
    Company_id = serializers.IntegerField() 
    CompanyName = serializers.CharField(max_length=500)     
    CreatedBy=    serializers.IntegerField()

class M_RoleAccessSerializerNewUpdated(serializers.Serializer):
    id = serializers.IntegerField()
    moduleid = serializers.IntegerField()
    ModuleName = serializers.CharField(max_length=500)
    pageid = serializers.IntegerField() 
    RelatedPageID = serializers.IntegerField() 
    PageName = serializers.CharField(max_length=500)

class MC_RolePageAccessSerializerNewUpdated(serializers.Serializer):
    
    id=serializers.IntegerField()
    Name = serializers.CharField(max_length=500)

class M_PageAccessSerializerNewUpdated(serializers.Serializer):
    
    id=serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
   
class M_PageSerializerNewUpdated(serializers.Serializer):
    id=serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    
    
class M_PageSerializerAddPage(serializers.Serializer):
    moduleid = serializers.IntegerField()
    ModuleName = serializers.CharField(max_length=500)
    id = serializers.IntegerField() 
    RelatedPageID = serializers.IntegerField() 
    PageName = serializers.CharField(max_length=500)
    
class M_PageAccessSerializerAddPage(serializers.Serializer):
    
    id=serializers.IntegerField()
    Name = serializers.CharField(max_length=500)             
   


class CopyRoleAccessSerializer(serializers.ModelSerializer):
    RoleAccess=MC_RolePageAccessSerilaizer(many=True)

    class Meta:
        model = M_RoleAccess
        fields = ['Company','Modules','Pages','RoleAccess','CreatedBy','UpdatedBy']


class InsertCopyRoleAccessSerializer(serializers.ModelSerializer):
    RoleAccess=MC_RolePageAccessSerilaizer(many=True)

    class Meta:
        model = M_RoleAccess
        fields = ['Role','Company','Division','Modules','Pages','RoleAccess','CreatedBy','UpdatedBy']    
    def create(self, validated_data):
        
        CopyRolePageAccess_datalist = validated_data.pop('RoleAccess')
        RoleAccessID = M_RoleAccess.objects.create(**validated_data)
        for RolePageAccess_data in CopyRolePageAccess_datalist:
           MC_RolePageAccess.objects.create(RoleAccess=RoleAccessID, **RolePageAccess_data)
        return RoleAccessID    

        
class RoleAccessserializerforsidemenu(serializers.ModelSerializer):
    Pages=M_PagesSerializer2()
    
    class Meta:
        model= M_RoleAccess
        fields ="__all__" 

class RoleAccessserializerDeleteView(serializers.ModelSerializer):
    class Meta:
        model= M_RoleAccess
        fields ="__all__"         