from dataclasses import field
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
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
                HPagesdata = M_Pages.objects.raw('''SELECT p.ID,p.Name,p.Description,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,
Rp.Name RelatedPageName 
FROM M_Pages p 
join H_Modules m on p.Module_id= m.ID
left join M_Pages RP on p.RelatedPageID=RP.id ''')
                
                HPagesserialize_data = M_PagesSerializer(HPagesdata, many=True).data
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': HPagesserialize_data})
                
        except Exception as e:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})



    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                HPagesdata = JSONParser().parse(request)
                HPagesserialize_data = M_PagesSerializer1(data=HPagesdata)
                if HPagesserialize_data.is_valid():
                    HPagesserialize_data.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Page Save Successfully','Data': HPagesserialize_data.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': HPagesserialize_data.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class M_PagesViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                HPagesdata = M_Pages.objects.raw('''SELECT p.ID,p.Name,p.Description,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,p.RelatedPageID,
Rp.Name RelatedPageName 
FROM M_Pages p 
join H_Modules m on p.Module_id= m.ID
left join M_Pages RP on p.RelatedPageID=RP.id where p.ID= %s''', [id])
                # if HPagesdata.exists():
                PageListData=list()
                HPagesserialize_data = M_PagesSerializer(HPagesdata, many=True).data
                for a in HPagesserialize_data:
                    # bb=MC_PagePageAccess.objects.filter(PageID=id)
                    bb=MC_PagePageAccess.objects.raw('''SELECT mc_pagepageaccess.AccessID_id ID,h_pageaccess.Name Name FROM mc_pagepageaccess join h_pageaccess on h_pageaccess.ID=mc_pagepageaccess.AccessID_id where mc_pagepageaccess.PageID_id=%s''', [id])
                    MC_PagePageAccess_data = MC_PagePageAccessSerializer(bb, many=True).data
                    PageAccessListData=list()
                    for b in MC_PagePageAccess_data:
                        PageAccessListData.append({
                            "AccessID" : b['ID'],
                            "AccessName" : b['Name']
                        })
                    
                    PageListData.append({
                        
                        "ID": a['ID'],
                        "Name": a['Name'],
                        "Description": a['Description'],
                        "Module": a['ModuleID'],
                        "ModuleName": a['ModuleName'],
                        "isActive": a['isActive'],
                        "DisplayIndex": a['DisplayIndex'],
                        "Icon": a['Icon'],
                        "ActualPagePath": a['ActualPagePath'],
                        "isShowOnMenu": a['isShowOnMenu'],
                        "PageType": a['PageType'],
                        "RelatedPageID": a['RelatedPageID'],
                        "RelatedPageName": a['RelatedPageName'],
                        "PagePageAccess": PageAccessListData
                    }) 
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': PageListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Pagesdata = JSONParser().parse(request)
                PagesdataByID = M_Pages.objects.get(ID=id)
                Pages_Serializer = M_PagesSerializer1(PagesdataByID, data=Pagesdata)
                if Pages_Serializer.is_valid():
                    Pages_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Page Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Pages_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = M_Pages.objects.get(ID=id)
                Modulesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' Page Deleted Successfully'})
        except Exception as e:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})  


class showPagesListOnPageType(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                HPagesdata = M_Pages.objects.filter(PageType=id)
                HPagesserialize_data = M_PagesSerializer1(HPagesdata,many=True).data
                HPageListData = list()
                for a1 in HPagesserialize_data:
                    HPageListData.append({
                    'ID':a1["ID"],
                    'Name':a1["Name"]
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':HPageListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e), 'Data':[]})
                    
