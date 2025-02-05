from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Pages import *
from ..models import M_Pages
from django.db.models import OuterRef, Subquery


class M_PageTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PageType_data = M_PageType.objects.all()
                if PageType_data.exists():
                    PageType_serializer = PageTypeMasterSerializer(PageType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageType_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Page Type Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class M_PagesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_Pages.objects.raw('''SELECT p.id,p.Name,p.PageHeading,p.PageDescription,p.PageDescriptionDetails,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,p.IsDivisionRequired,p.IsEditPopuporComponent,p.CountLabel,p.ShowCountLabel,RP.Name RelatedPageName,M_PageType.Name PageTypeName,p.IsSweetPOSPage FROM M_Pages p join H_Modules m on p.Module_id= m.ID left join M_Pages RP on p.RelatedPageID=RP.id join M_PageType on M_PageType.id= p.pagetype  Order By m.DisplayIndex,p.DisplayIndex ''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    HPagesserialize_data = M_PagesSerializer(
                        query, many=True).data 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': HPagesserialize_data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                HPagesdata = JSONParser().parse(request)
                HPagesserialize_data = M_PagesSerializer1(data=HPagesdata)
                if HPagesserialize_data.is_valid():
                    HPagesserialize_data.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Page Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': HPagesserialize_data.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class M_PagesViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                # HPagesdata = M_Pages.objects.raw('''SELECT p.id,p.Name,p.PageHeading,p.PageDescription,p.PageDescriptionDetails,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,p.IsDivisionRequired,p.IsEditPopuporComponent,p.CountLabel,p.ShowCountLabel,RP.Name RelatedPageName,M_PageType.Name PageTypeName 
                # FROM M_Pages p 
                # join H_Modules m on p.Module_id= m.ID 
                # left join M_Pages RP on p.RelatedPageID=RP.id 
                # join M_PageType on M_PageType.id= p.pagetype where p.id= %s''', [id])
                subquery = M_PageType.objects.filter(id=OuterRef('PageType')).values('Name')[:1]
                subquery1 = M_Pages.objects.filter(id=OuterRef('RelatedPageID')).values('Name')[:1]
                HPagesdata = M_Pages.objects.select_related('Module').filter(id=id
                ).annotate(PageTypeName=Subquery(subquery)).annotate(RelatedPageName=Subquery(subquery1)).values(
    'id',
    'Name',
    'PageHeading',
    'PageDescription',
    'PageDescriptionDetails',
    'isActive',
    'DisplayIndex',
    'Icon',
    'ActualPagePath',
    'Module__id',
    'Module__Name',
    'PageType',
    'PageTypeName',
    'RelatedPageID',
    'RelatedPageName',
    'IsDivisionRequired',
    'IsEditPopuporComponent',
    'CountLabel',
    'ShowCountLabel',
    'CreatedBy',
    'CreatedOn',
    'UpdatedBy',
    'UpdatedOn',
    # add IsSweetPOSPage flag
    'IsSweetPOSPage' 
)
                
                if not HPagesdata: 
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:     
                    PageListData = list()
                    # HPagesserialize_data = M_PagesSerializer(
                    #     HPagesdata, many=True).data
                    for a in HPagesdata:
                        # bb=MC_PagePageAccess.objects.filter(PageID=id)
#                         bb = MC_PagePageAccess.objects.raw('''SELECT MC_PagePageAccess.Access_id id,H_PageAccess.Name Name 
# FROM MC_PagePageAccess 
# join H_PageAccess on H_PageAccess.ID=MC_PagePageAccess.Access_id 
# where MC_PagePageAccess.Page_id=%s''', [id])
                        bb = MC_PagePageAccess.objects.filter(Page_id=id).select_related('Access').values(
                                                'Access_id',
                                                'Access__Name'
                                            )
                        # MC_PagePageAccess_data = MC_PagePageAccessSerializer(
                        #     bb, many=True).data
                        PageAccessListData = list()
                        for b in bb:
                            PageAccessListData.append({
                                "AccessID": b['Access_id'],
                                "AccessName": b['Access__Name']
                            })
                        # bb=id
                        aa=M_Pages.objects.filter(id=id).values('RelatedPageID')
                        
                        if(aa[0]['RelatedPageID']  == 0):
                            bb=id
                        else:
                            bb= aa[0]['RelatedPageID']

                        
                        # MasterPageFieldQuery = MC_PageFieldMaster.objects.raw('''SELECT MC_PageFieldMaster.id, ControlID, FieldLabel, IsCompulsory, DefaultSort, ListPageSeq, ShowInListPage, ShowInDownload, DownloadDefaultSelect,InValidMsg,MC_PageFieldMaster.ControlType_id,M_ControlTypeMaster.Name CName, FieldValidation_id,M_FieldValidations.Name FName,M_FieldValidations.RegularExpression,Alignment FROM MC_PageFieldMaster JOIN M_ControlTypeMaster on M_ControlTypeMaster.id=MC_PageFieldMaster.ControlType_id JOIN M_FieldValidations on M_FieldValidations.id=MC_PageFieldMaster.FieldValidation_id where MC_PageFieldMaster.Page_id=%s''', [bb])
                        MasterPageFieldQuery = MC_PageFieldMaster.objects.filter(Page_id=bb).select_related(
    'ControlType', 'FieldValidation'
).values(
    'id',
    'ControlID',
    'FieldLabel',
    'IsCompulsory',
    'DefaultSort',
    'ListPageSeq',
    'ShowInListPage',
    'ShowInDownload',
    'DownloadDefaultSelect',
    'InValidMsg',
    'ControlType__id',
    'ControlType__Name',
    'FieldValidation__id',
    'FieldValidation__Name',
    'FieldValidation__RegularExpression',
    'Alignment'
)
                        
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(PageFieldQuery.query)})

                        # MC_PageFieldMaster_data = MC_PageFieldMasterSerializerSecond(
                        #     MasterPageFieldQuery, many=True).data
                        
                        MC_PageFieldMasterListData = list()
                        for c in MasterPageFieldQuery:
                            
                            FieldValidationsdata = M_FieldValidations.objects.filter(ControlType=c['ControlType__id'])
                            FieldValidations_Serializer = FieldValidationsSerializer(FieldValidationsdata, many=True).data
                           
                            MC_PageFieldMasterListData.append({
                                
                                "ControlID":  c['ControlID'],
                                "ControlType":  c['ControlType__id'],
                                "ControlTypeName":c['ControlType__Name'],
                                "FieldLabel": c['FieldLabel'],
                                "IsCompulsory":c['IsCompulsory'],
                                "DefaultSort":c['DefaultSort'],      
                                "FieldValidation": c['FieldValidation__id'], 
                                "FieldValidationName":c['FieldValidation__Name'],      
                                "ListPageSeq": c['ListPageSeq'],
                                "ShowInListPage": c['ShowInListPage'],
                                "ShowInDownload": c['ShowInDownload'],
                                "ShownloadDefaultSelect":c['DownloadDefaultSelect'],
                                "RegularExpression":c['FieldValidation__RegularExpression'],
                                "InValidMsg":c['InValidMsg'],
                                "Alignment":c['Alignment'],
                                "FieldValidationlist":FieldValidations_Serializer
                                
                            })
                        
                        MC_PageFieldListData = list()
                        
                        if(a['PageType']== 2):
                            # ListPageFieldQuery = MC_PageFieldMaster.objects.raw('''SELECT MC_PageFieldMaster.id, ControlID, FieldLabel, IsCompulsory, DefaultSort, ListPageSeq, ShowInListPage, ShowInDownload, DownloadDefaultSelect,InValidMsg,MC_PageFieldMaster.ControlType_id,M_ControlTypeMaster.Name CName, FieldValidation_id,M_FieldValidations.Name FName,M_FieldValidations.RegularExpression,Alignment FROM MC_PageFieldMaster JOIN M_ControlTypeMaster on M_ControlTypeMaster.id=MC_PageFieldMaster.ControlType_id JOIN M_FieldValidations on M_FieldValidations.id=MC_PageFieldMaster.FieldValidation_id where MC_PageFieldMaster.Page_id=%s''', [id])
                            ListPageFieldQuery = (
    MC_PageFieldMaster.objects
    .filter(Page_id=id)
    .select_related('ControlType', 'FieldValidation')
    .values(
        'id',
        'ControlID',
        'FieldLabel',
        'IsCompulsory',
        'DefaultSort',
        'ListPageSeq',
        'ShowInListPage',
        'ShowInDownload',
        'DownloadDefaultSelect',
        'InValidMsg',
        'ControlType__id',
        'ControlType__Name',
        'FieldValidation__id',
        'FieldValidation__Name',
        'FieldValidation__RegularExpression',
        'Alignment'
    )
)
                            # MC_PageFieldMaster_data = MC_PageFieldMasterSerializerSecond(
                            #     ListPageFieldQuery, many=True).data
                            
                            
                            for c in ListPageFieldQuery:
                                FieldValidationsdata = M_FieldValidations.objects.filter(ControlType=c['ControlType__id'])
                                FieldValidations_Serializer = FieldValidationsSerializer(FieldValidationsdata, many=True).data
                                
                                MC_PageFieldListData.append({
                                    
                                    "ControlID":  c['ControlID'],
                                    "ControlType":  c['ControlType__id'],
                                    "ControlTypeName":c['ControlType__Name'],
                                    "FieldLabel": c['FieldLabel'],
                                    "IsCompulsory":c['IsCompulsory'],
                                    "DefaultSort":c['DefaultSort'],      
                                    "FieldValidation": c['FieldValidation__id'], 
                                    "FieldValidationName":c['FieldValidation__Name'],      
                                    "ListPageSeq": c['ListPageSeq'],
                                    "ShowInListPage": c['ShowInListPage'],
                                    "ShowInDownload": c['ShowInDownload'],
                                    "ShownloadDefaultSelect":c['DownloadDefaultSelect'],
                                    "RegularExpression":c['FieldValidation__RegularExpression'],
                                    "InValidMsg":c['InValidMsg'],
                                    "Alignment":c['Alignment'],
                                    "FieldValidationlist":FieldValidations_Serializer
                                    
                                })     
                        
                        PageListData.append({

                            "id": a['id'],
                            "Name": a['Name'],
                            "PageHeading": a['PageHeading'],
                            "PageDescription": a['PageDescription'],
                            "PageDescriptionDetails": a['PageDescriptionDetails'],
                            "Module": a['Module__id'],
                            "ModuleName": a['Module__Name'],
                            "isActive": a['isActive'],
                            "DisplayIndex": a['DisplayIndex'],
                            "Icon": a['Icon'],
                            "ActualPagePath": a['ActualPagePath'],
                            "PageType": a['PageType'],
                            "PageTypeName": a['PageTypeName'],
                            "RelatedPageId": a['RelatedPageID'],
                            "RelatedPageName": a['RelatedPageName'],
                            "IsDivisionRequired":a['IsDivisionRequired'],
                            "IsEditPopuporComponent":a['IsEditPopuporComponent'],
                            "CountLabel":a['CountLabel'],
                            "ShowCountLabel":a['ShowCountLabel'],
                            "PagePageAccess": PageAccessListData,
                            "PageFieldMaster": MC_PageFieldMasterListData,
                            "PageFieldList" : MC_PageFieldListData,
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            # add IsSweetPOSPage Flag
                            "IsSweetPOSPage":a['IsSweetPOSPage'],
                        })  
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageListData[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Pagesdata = JSONParser().parse(request)
                PagesdataByID = M_Pages.objects.get(id=id)
                Pages_Serializer = M_PagesSerializer1(
                    PagesdataByID, data=Pagesdata)
                if Pages_Serializer.is_valid():
                    Pages_Serializer.save() 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Page Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Pages_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = M_Pages.objects.get(id=id)
                Modulesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' Page Deleted Successfully', 'Data': []})
        except M_Pages.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Page Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Page used in another table', 'Data': []})

class showPagesListOnPageType(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                HPagesdata = M_Pages.objects.filter(PageType=1)
                HPagesserialize_data = M_PagesSerializer1(
                    HPagesdata, many=True).data
                HPageListData = list()
                for a1 in HPagesserialize_data:
                    HPageListData.append({
                        'id': a1["id"],
                        'Name': a1["Name"]
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': HPageListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class PagesMasterForRoleAccessView(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                HPagesdata = M_Pages.objects.raw('''SELECT p.id,p.Name,p.PageHeading,p.PageDescription,p.PageDescriptionDetails,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,
RP.Name RelatedPageName 
FROM M_Pages p 
join H_Modules m on p.Module_id= m.ID
left join M_Pages RP on p.RelatedPageID=RP.id where p.id= %s''', [id])
                if not HPagesdata:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:    
                    PageListData = list()
                    HPagesserialize_data = M_PagesSerializer(
                        HPagesdata, many=True).data
                    for a in HPagesserialize_data:
                        # bb=MC_PagePageAccess.objects.filter(PageID=id)
                        bb = MC_PagePageAccess.objects.raw('''SELECT MC_PagePageAccess.Access_id id,H_PageAccess.Name Name 
FROM MC_PagePageAccess 
join H_PageAccess on H_PageAccess.ID=MC_PagePageAccess.Access_id 
where MC_PagePageAccess.Page_id=%s''', [id])
                        MC_PagePageAccess_data = MC_PagePageAccessSerializer(
                            bb, many=True).data
                        PageAccessListData = list()
                        for b in MC_PagePageAccess_data:
                            PageAccessListData.append({
                                "id": b['id'],
                                "Name": b['Name']
                            })

                        PageListData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "DisplayIndex": a['DisplayIndex'],
                            "Icon": a['Icon'],
                            "ActualPagePath": a['ActualPagePath'],
                            # "isShowOnMenu": a['isShowOnMenu'],
                            "RolePageAccess": PageAccessListData
                        })
                    PageListData = {
                "ModuleID": a['ModuleID'],
                "ModuleName": a['ModuleName'],
                "ModuleData": PageListData,}
                        
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':[PageListData] })
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class ControlTypeMasterView(CreateAPIView):    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                ControlTypedata = M_ControlTypeMaster.objects.all()
                if ControlTypedata.exists():
                    ControlTypedata_Serializer = ControlTypeMasterSerializer(ControlTypedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ControlTypedata_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'ControlTypes Not Available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class FieldValidationsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                FieldValidationsdata = M_FieldValidations.objects.filter(ControlType=id)
                if FieldValidationsdata.exists():
                    FieldValidations_Serializer = FieldValidationsSerializer(FieldValidationsdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': FieldValidations_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Field Validations Not Available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})  
        
        
class FieldValidationsViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        try:
            with transaction.atomic():
                Field_data = JSONParser().parse(request)
                Field_Validations_serializer = FieldValidationsSerializerSecond(data=Field_data)
                if Field_Validations_serializer.is_valid():
                    Field_Validations_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Field Data Uploaded Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Field_Validations_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                
                Field_data = M_FieldValidations.objects.all()
         
                Field_Validations_serializer = FieldValidationsSerializerSecond(Field_data,many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Field_Validations_serializer.data})
        except  M_FieldValidations.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  ' Field Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
    
class FieldValidationsViewThird(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Field_data = M_FieldValidations.objects.get(id=id)
                Field_Validations_serializer = FieldValidationsSerializerSecond(Field_data)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Field_Validations_serializer.data})
        except  M_FieldValidations.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Field Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Field_data = JSONParser().parse(request)
                Field_dataByID = M_FieldValidations.objects.get(id=id)
                Field_Validations_serializer = FieldValidationsSerializerSecond(
                    Field_dataByID, data=Field_data)
                if Field_Validations_serializer.is_valid():
                    Field_Validations_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Field Data Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Field_Validations_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Field_data = M_FieldValidations.objects.get(id=id)
                Field_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Field Data Deleted Successfully','Data':[]})
        except M_FieldValidations.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Field Data Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Field Data used in another table', 'Data': []})
        
