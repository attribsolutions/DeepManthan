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
        # def get(self, request, Role=0):
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
            query = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id,m_pages.Name,m_pages.PageHeading,m_pages.PageDescription,m_pages.PageDescriptionDetails,m_pages.ActualPagePath,m_pages.DisplayIndex,
m_pages.Icon,m_pages.isActive,m_pages.Module_id,
m_pages.PageType,m_pages.RelatedPageID,Pages_id FROM m_roleaccess
JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id 
WHERE Role_id=%s AND  Modules_id=%s and Division_id=%s and Company_id=%s  ''', ([Role], [id],[Division],[Company]))

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
                    "RelatedPageID": a1['RelatedPageID'],
                    "Name": a1['Name'],
                    "PageHeading": a1['PageHeading'],
                    "PageDescription": a1['PageDescription'],
                    "PageDescriptionDetails": a1['PageDescriptionDetails'],
                    "DisplayIndex": a1['DisplayIndex'],
                    "Icon": a1['Icon'],
                    "ActualPagePath": a1['ActualPagePath'],
                    # "isShowOnMenu": a1['isShowOnMenu'],
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
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data': []})


class RoleAccessViewList(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id,M_RoleAccess.Role_id,M_Roles.Name RoleName,M_RoleAccess.Division_id,M_Parties.Name DivisionName,M_RoleAccess.Company_id,C_Companies.Name CompanyName
    FROM M_RoleAccess
    join M_Roles ON M_Roles.id=M_RoleAccess.Role_id
    join M_Parties  ON M_Parties.id=M_RoleAccess.Division_id
    join C_Companies  ON C_Companies.id=M_RoleAccess.Company_id  group by Role_id,Division_id,Company_id''')
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    M_Items_Serializer = M_RoleAccessSerializerGETList(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Items_Serializer})

        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})


class RoleAccessViewNewUpdated(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request,Role=0,Division=0):
        roleaccessquery = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id id, h_modules.id moduleid, h_modules.Name ModuleName,m_pages.id pageid,m_pages.RelatedPageID, m_pages.name PageName  FROM m_roleaccess JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id JOIN h_modules ON h_modules.id=m_roleaccess.Modules_id WHERE m_pages.PageType=2 AND Role_id=%s AND Division_id=%s   ''',([Role],[Division]))
        # return JsonResponse({'query':  str(roleaccessquery.query)})
        RoleAccessdata = M_RoleAccessSerializerNewUpdated(roleaccessquery, many=True).data
        # return JsonResponse({'data':  RoleAccessdata})
       
        Moduledata = list()

        for a in RoleAccessdata:
            id = a['id']
            pageid=a['pageid']
            RelatedPageID=a['RelatedPageID']

            RelatedPageroleaccessquery = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id id,'a' as Name FROM m_roleaccess WHERE  Pages_id=%s and  Role_id=%s AND Division_id=%s    ''',([RelatedPageID],[Role],[Division]))
            RelatedPageRoleAccessdata = MC_RolePageAccessSerializerNewUpdated(RelatedPageroleaccessquery, many=True).data
            # return JsonResponse({'data':  RelatedPageRoleAccessdata})
            roleaccessID=RelatedPageRoleAccessdata[0]['id']
            rolepageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_rolepageaccess.PageAccess_id,0) id from h_pageaccess left JOIN mc_rolepageaccess ON mc_rolepageaccess.PageAccess_id=h_pageaccess.id AND mc_rolepageaccess.RoleAccess_id=%s ''', [roleaccessID])
            # return JsonResponse({'query':  str(rolepageaccessquery.query)})
            RolePageAccessSerializer = MC_RolePageAccessSerializerNewUpdated(rolepageaccessquery,  many=True).data
            # return JsonResponse({'data':  RolePageAccessSerializer})
            pageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_pagepageaccess.Access_id,0) id from h_pageaccess left JOIN mc_pagepageaccess ON mc_pagepageaccess.Access_id=h_pageaccess.id AND mc_pagepageaccess.Page_id=%s order by Sequence''', [pageid])
            # return JsonResponse({'query':  str(pageaccessquery.query)})
            PageAccessSerializer = M_PageAccessSerializerNewUpdated(pageaccessquery,  many=True).data
            Moduledata.append({
                "ModuleID": a['moduleid'],
                "ModuleName": a['ModuleName'],
                "PageID": a['pageid'],
                "RelatedPageID": a['RelatedPageID'],
                "PageName": a['PageName'],
                "RoleAccess_IsShowOnMenu": RolePageAccessSerializer[0]['id'],
                "RoleAccess_IsSave": RolePageAccessSerializer[1]['id'],
                "RoleAccess_IsView": RolePageAccessSerializer[2]['id'],
                "RoleAccess_IsEdit": RolePageAccessSerializer[3]['id'],
                "RoleAccess_IsDelete": RolePageAccessSerializer[4]['id'],
                "RoleAccess_IsEditSelf": RolePageAccessSerializer[5]['id'],
                "RoleAccess_IsDeleteSelf": RolePageAccessSerializer[6]['id'],
                "RoleAccess_IsPrint": RolePageAccessSerializer[7]['id'],
                "RoleAccess_IsTopOfTheDivision": RolePageAccessSerializer[8]['id'],
                "PageAccess_IsShowOnMenu": PageAccessSerializer[0]['id'],
                "PageAccess_IsSave": PageAccessSerializer[1]['id'],
                "PageAccess_IsView": PageAccessSerializer[2]['id'],
                "PageAccess_IsEdit": PageAccessSerializer[3]['id'],
                "PageAccess_IsDelete": PageAccessSerializer[4]['id'],
                "PageAccess_IsEditSelf": PageAccessSerializer[5]['id'],
                "PageAccess_IsDeleteSelf": PageAccessSerializer[6]['id'],
                "PageAccess_IsPrint": PageAccessSerializer[7]['id'],
                "PageAccess_IsTopOfTheDivision": PageAccessSerializer[8]['id']

            })

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        return Response(response)

class RoleAccessViewAddPage(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, pageid=0):
        roleaccessquery = M_Pages.objects.raw('''SELECT h_modules.id moduleid, h_modules.Name ModuleName,m_pages.id id,m_pages.RelatedPageID, m_pages.name PageName FROM m_pages JOIN h_modules ON h_modules.id=m_pages.Module_id WHERE m_pages.id=%s''',[pageid])
        # return JsonResponse({'query':  str(roleaccessquery.query)})
        RoleAccessdata = M_PageSerializerAddPage(roleaccessquery, many=True).data
        # return JsonResponse({'data':  RoleAccessdata})
        Moduledata = list()
        for a in RoleAccessdata:
            pageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_pagepageaccess.Access_id,0) id from h_pageaccess left JOIN mc_pagepageaccess ON mc_pagepageaccess.Access_id=h_pageaccess.id AND mc_pagepageaccess.Page_id=%s order by Sequence''', [pageid])
            # return JsonResponse({'query':  str(pageaccessquery.query)})
            PageAccessSerializer = M_PageAccessSerializerAddPage(pageaccessquery,many=True).data
            Moduledata.append({
                "ModuleID": a['moduleid'],
                "ModuleName": a['ModuleName'],
                "PageID": a['id'],
                "RelatedPageID": a['RelatedPageID'],
                "PageName": a['PageName'],
                "RoleAccess_IsShowOnMenu": 0,
                "RoleAccess_IsSave": 0,
                "RoleAccess_IsView": 0,
                "RoleAccess_IsEdit": 0,
                "RoleAccess_IsDelete": 0,
                "RoleAccess_IsEditSelf": 0,
                "RoleAccess_IsDeleteSelf": 0,
                "RoleAccess_IsPrint": 0,
                "RoleAccess_IsTopOfTheDivision": 0,
                "PageAccess_IsShowOnMenu": PageAccessSerializer[0]['id'],
                "PageAccess_IsSave": PageAccessSerializer[1]['id'],
                "PageAccess_IsView": PageAccessSerializer[2]['id'],
                "PageAccess_IsEdit": PageAccessSerializer[3]['id'],
                "PageAccess_IsDelete": PageAccessSerializer[4]['id'],
                "PageAccess_IsEditSelf": PageAccessSerializer[5]['id'],
                "PageAccess_IsDeleteSelf": PageAccessSerializer[6]['id'],
                "PageAccess_IsPrint": PageAccessSerializer[7]['id'],
                "PageAccess_IsTopOfTheDivision": PageAccessSerializer[8]['id']
                 
            })

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        return Response(response)    

class RoleAccessGetPagesOnModule(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, moduleid=0):
        try:
            with transaction.atomic():
                query = M_Pages.objects.raw('''Select m_pages.id,m_pages.Name FROM m_pages  WHERE m_pages.PageType=2 and   Module_id=%s''',[moduleid])
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    PageSerializer = M_PageSerializerNewUpdated(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageSerializer})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})
        
        
class RoleAccessGetPagesAccessOnPage(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, moduleid=0):
        try:
            with transaction.atomic():
                query = M_Pages.objects.raw('''Select m_pages.id,m_pages.Name FROM m_pages  WHERE Module_id=%s''',[moduleid])
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    PageSerializer = M_PageSerializerNewUpdated(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageSerializer})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})        
       


class CopyRoleAccessView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):       
        Role = request.data['Role']
        Division  = request.data['Division']
        NewRole = request.data['NewRole']
        NewDivision = request.data['NewDivision']
        try:
            with transaction.atomic():
                CopyRoleAccessdata = M_RoleAccess.objects.filter(Role_id= Role,Division_id =Division)
                if CopyRoleAccessdata.exists():
                    serializersdata = CopyRoleAccessSerializer(CopyRoleAccessdata, many=True)
                    additionaldata=list()
                    for a in serializersdata.data:
                        a.update({'Role': NewRole,'Division':NewDivision})
                        additionaldata.append(a)
                    # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':additionaldata})    
                    RoleAccessSerialize_data = InsertCopyRoleAccessSerializer(data=additionaldata, many=True)
                    if RoleAccessSerialize_data.is_valid():
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':RoleAccessSerialize_data.data}) 
                        RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                            Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':str(RoleAccessdata.query)}) 
                        RoleAccessdata.delete()
                        RoleAccessSerialize_data.save()
                    
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Copy Role Access Save Successfully', 'Data': []})
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Execution Error', 'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data': []})