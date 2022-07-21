from urllib import response
from django.http import JsonResponse
from rest_framework.response import Response

from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_RoleAccess import *
from ..models import *


class RoleAccessView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, Role=0, Division=0, Company=0):
        modules = M_RoleAccess.objects.raw(
            '''SELECT distinct Modules_id id ,h_modules.id, h_modules.Name,h_modules.DisplayIndex 
FROM m_roleaccess 
join h_modules on h_modules.id=m_roleaccess.Modules_id
where Role_id =%s AND M_RoleAccess.Division_id=%s AND M_RoleAccess.Company_id=%s
ORDER BY h_modules.DisplayIndex''', ([Role], [Division], [Company]))
        data = M_RoleAccessSerializerfordistinctModule(modules, many=True).data
        Moduledata = list()
        for a in data:
            id = a['id']
            query = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id,m_pages.Name,m_pages.Description,m_pages.ActualPagePath,m_pages.DisplayIndex,
m_pages.Icon,m_pages.isActive,m_pages.isShowOnMenu,m_pages.Module_id,
m_pages.PageType,m_pages.RelatedPageID, 
Pages_id FROM erpdatabase.m_roleaccess
JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id 
WHERE Role_id=%s AND  Modules_id=%s ''', ([Role], [id]))

            PageSerializer = M_PagesSerializerforRoleAccessNEW(
                query,  many=True).data
            Pagesdata = list()
            for a1 in PageSerializer:
                id = a1['id']
                RolePageAccess = MC_RolePageAccess.objects.raw(''' SELECT mc_rolepageaccess.PageAccess_id id,Name  FROM mc_rolepageaccess 
                JOIN h_pageaccess ON h_pageaccess.id=mc_rolepageaccess.PageAccess_id  WHERE mc_rolepageaccess.RoleAccess_id=%s ''', [id])
                RolePageAccessSerializer = MC_RolePageAccessSerializer(
                    RolePageAccess,  many=True).data
                Pagesdata.append({
                    "id": a1['Pages_id'],
                    "Name": a1['Name'],
                    "DisplayIndex": a1['DisplayIndex'],
                    "Icon": a1['Icon'],
                    "ActualPagePath": a1['ActualPagePath'],
                    "isShowOnMenu": a1['isShowOnMenu'],
                    "RolePageAccess": RolePageAccessSerializer
                })

            response1 = {
                "ModuleID": a['id'],
                "ModuleName": a['Name'],
                "ModuleData": Pagesdata,

            }
            Moduledata.append(response1)

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        return Response(response)

    # Role Access POST Method first delete record on role,company,division and then Insert data

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                RoleAccessdata = JSONParser().parse(request)
                RoleAccessSerialize_data = M_RoleAccessSerializer(
                    data=RoleAccessdata, many=True)
                if RoleAccessSerialize_data.is_valid():
                    # return JsonResponse({'Data':RoleAccessSerialize_data.data[0]['Role']})
                    RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                        Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                    RoleAccessdata.delete()
                    RoleAccessSerialize_data.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Access Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class RoleAccessViewList(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id,M_Roles.Name RoleName,M_DivisionType.Name DivisionName,C_Companies.Name CompanyName
    FROM M_RoleAccess
    join M_Roles ON M_Roles.id=M_RoleAccess.Role_id
    join M_DivisionType  ON M_DivisionType.id=M_RoleAccess.Division_id
    join C_Companies  ON C_Companies.id=M_RoleAccess.Company_id group by Role_id,Company_id,Division_id''')
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    M_Items_Serializer = M_RoleAccessSerializerGETList(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Items_Serializer})

        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class RoleAccessViewNewUpdated(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, Role=0, Division=0):
        roleaccessquery = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id id, h_modules.id moduleid, h_modules.Name ModuleName,m_pages.id pageid, m_pages.name PageName  FROM erpdatabase.m_roleaccess JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id JOIN h_modules ON h_modules.id=m_roleaccess.Modules_id WHERE Role_id=%s AND Division_id=%s''',([Role], [Division]))
        # return JsonResponse({'query':  str(roleaccessquery.query)})
        RoleAccessdata = M_RoleAccessSerializerNewUpdated(roleaccessquery, many=True).data
        # return JsonResponse({'data':  RoleAccessdata})
        Moduledata = list()
        for a in RoleAccessdata:
            id = a['id']
            pageid=a['pageid']
            rolepageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_rolepageaccess.PageAccess_id,0) id from h_pageaccess left JOIN mc_rolepageaccess ON mc_rolepageaccess.PageAccess_id=h_pageaccess.id AND mc_rolepageaccess.RoleAccess_id=%s ''', [id])
            # return JsonResponse({'query':  str(rolepageaccessquery.query)})
            RolePageAccessSerializer = MC_RolePageAccessSerializerNewUpdated(rolepageaccessquery,  many=True).data
            # return JsonResponse({'data':  RolePageAccessSerializer})
            pageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_pagepageaccess.Access_id,0) id from h_pageaccess left JOIN mc_pagepageaccess ON mc_pagepageaccess.Access_id=h_pageaccess.id AND mc_pagepageaccess.Page_id=%s ''', [pageid])
            # return JsonResponse({'query':  str(pageaccessquery.query)})
            PageAccessSerializer = M_PageAccessSerializerNewUpdated(pageaccessquery,  many=True).data
            Moduledata.append({
                "ModuleID": a['moduleid'],
                "ModuleName": a['ModuleName'],
                "PageID": a['pageid'],
                "PageName": a['PageName'],
                "RoleAccess_IsSave": RolePageAccessSerializer[0]['id'],
                "RoleAccess_IsEdit": RolePageAccessSerializer[1]['id'],
                "RoleAccess_IsDelete": RolePageAccessSerializer[2]['id'],
                "RoleAccess_IsEditSelf": RolePageAccessSerializer[3]['id'],
                "RoleAccess_IsDeleteSelf": RolePageAccessSerializer[4]['id'],
                "RoleAccess_IsShow": RolePageAccessSerializer[5]['id'],
                "RoleAccess_IsView": RolePageAccessSerializer[6]['id'],
                "RoleAccess_IsTopOfTheDivision": RolePageAccessSerializer[7]['id'],
                "PageAccess_IsSave": PageAccessSerializer[0]['id'],
                "PageAccess_IsEdit": PageAccessSerializer[1]['id'],
                "PageAccess_IsDelete": PageAccessSerializer[2]['id'],
                "PageAccess_IsEditSelf": PageAccessSerializer[3]['id'],
                "PageAccess_IsDeleteSelf": PageAccessSerializer[4]['id'],
                "PageAccess_IsShow": PageAccessSerializer[5]['id'],
                "PageAccess_IsView": PageAccessSerializer[6]['id'],
                "PageAccess_IsTopOfTheDivision": PageAccessSerializer[7]['id']

            })

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        return Response(response)

   
