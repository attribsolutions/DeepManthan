from dataclasses import field
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Pages import *

from ..models import M_Pages


class M_PagesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_Pages.objects.raw('''SELECT p.id,p.Name,p.PageHeading,p.PageDescription,p.PageDescriptionDetails,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,p.IsDivisionRequired,
Rp.Name RelatedPageName 
FROM M_Pages p 
join H_Modules m on p.Module_id= m.ID
left join M_Pages RP on p.RelatedPageID=RP.id Order By m.DisplayIndex,p.DisplayIndex ''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    HPagesserialize_data = M_PagesSerializer(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': HPagesserialize_data})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' Execution Error', 'Data': []})

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
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data': []})


class M_PagesViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                HPagesdata = M_Pages.objects.raw('''SELECT p.id,p.Name,p.PageHeading,p.PageDescription,p.PageDescriptionDetails,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,p.IsDivisionRequired,
Rp.Name RelatedPageName 
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
                        bb = MC_PagePageAccess.objects.raw('''SELECT mc_pagepageaccess.Access_id id,h_pageaccess.Name Name 
FROM mc_pagepageaccess 
join h_pageaccess on h_pageaccess.ID=mc_pagepageaccess.Access_id 
where mc_pagepageaccess.Page_id=%s''', [id])
                        MC_PagePageAccess_data = MC_PagePageAccessSerializer(
                            bb, many=True).data
                        PageAccessListData = list()
                        for b in MC_PagePageAccess_data:
                            PageAccessListData.append({
                                "AccessID": b['id'],
                                "AccessName": b['Name']
                            })

                        PageFieldQuery = MC_PageFieldMaster.objects.raw('''SELECT mc_pagefieldmaster.id, FieldLabel, IsCompulsory, ListPageSeq, ShowInListPage, ShowInDownload, DownloadDefaultSelect,
 ControlType_id,m_controltypemaster.Name CName, FieldValidation_id,m_fieldvalidations.Name FName FROM mc_pagefieldmaster
 JOIN m_controltypemaster on m_controltypemaster.id=mc_pagefieldmaster.ControlType_id
 JOIN m_fieldvalidations on m_fieldvalidations.id=mc_pagefieldmaster.FieldValidation_id 
 where mc_pagefieldmaster.Page_id=%s''', [id])
                        MC_PageFieldMaster_data = MC_PageFieldMasterSerializerSecond(
                            PageFieldQuery, many=True).data
                        MC_PageFieldMasterListData = list()
                        for c in MC_PageFieldMaster_data:
                            MC_PageFieldMasterListData.append({
                               
                                "ControlType":  c['ControlType_id'],
                                "ControlTypeName":c['CName'],
                                "FieldLabel": c['FieldLabel'],
                                "IsCompulsory":c['IsCompulsory'],      
                                "FieldValidation": c['FieldValidation_id'], 
                                "FieldValidationName":c['FName'],      
                                "ListPageSeq": c['ListPageSeq'],
                                "ShowInListPage": c['ShowInListPage'],
                                "ShowInDownload": c['ShowInDownload'],
                                "DownloadDefaultSelect":c['DownloadDefaultSelect'],
                            })
                        
                        
                        PageListData.append({

                            "id": a['id'],
                            "Name": a['Name'],
                            "PageHeading": a['PageHeading'],
                            "PageDescription": a['PageDescription'],
                            "PageDescriptionDetails": a['PageDescriptionDetails'],
                            "Module": a['ModuleID'],
                            "ModuleName": a['ModuleName'],
                            "isActive": a['isActive'],
                            "DisplayIndex": a['DisplayIndex'],
                            "Icon": a['Icon'],
                            "ActualPagePath": a['ActualPagePath'],
                            "PageType": a['PageType'],
                            "RelatedPageID": a['RelatedPageID'],
                            "RelatedPageName": a['RelatedPageName'],
                            "IsDivisionRequired":a['IsDivisionRequired'],
                            "PagePageAccess": PageAccessListData,
                            "PageFieldMaster": MC_PageFieldMasterListData
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageListData[0]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data': []})

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
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})

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
    authentication_class = JSONWebTokenAuthentication

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
        except Exception:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})

class PagesMasterForRoleAccessView(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                HPagesdata = M_Pages.objects.raw('''SELECT p.id,p.Name,p.PageHeading,p.PageDescription,p.PageDescriptionDetails,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,
Rp.Name RelatedPageName 
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
                        bb = MC_PagePageAccess.objects.raw('''SELECT mc_pagepageaccess.Access_id id,h_pageaccess.Name Name 
FROM mc_pagepageaccess 
join h_pageaccess on h_pageaccess.ID=mc_pagepageaccess.Access_id 
where mc_pagepageaccess.Page_id=%s''', [id])
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
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':'Execution Error', 'Data': []})

class ControlTypeMasterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
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
    authentication_class = JSONWebTokenAuthentication
    
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