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
    
    def get(self, request,id=0):
        
        modules = M_RoleAccess.objects.raw(
            '''SELECT distinct Modules_id id ,h_modules.id, h_modules.Name,h_modules.DisplayIndex 
FROM m_roleaccess 
join h_modules on h_modules.id=m_roleaccess.Modules_id
where Role_id =1 AND M_RoleAccess.Company_id=1 AND M_RoleAccess.Division_id=1 
ORDER BY h_modules.DisplayIndex''')
        data = M_RoleAccessSerializerfordistinctModule(modules, many=True).data
        Moduledata = list()
        for a in data:
            id=a['id']
            query=M_RoleAccess.objects.raw('''SELECT m_roleaccess.id,m_pages.Name,m_pages.Description,m_pages.ActualPagePath,m_pages.DisplayIndex,
m_pages.Icon,m_pages.isActive,m_pages.isShowOnMenu,m_pages.Module_id,
m_pages.PageType,m_pages.RelatedPageID, 
Pages_id FROM erpdatabase.m_roleaccess
JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id 
WHERE Role_id=1 AND  Modules_id=%s ''',[id])

           
            PageSerializer = M_PagesSerializerforRoleAccessNEW(query,  many=True).data
            Pagesdata = list()
            for a1 in PageSerializer:
                id=a1['id']
                RolePageAccess=MC_RolePageAccess.objects.raw(''' SELECT mc_rolepageaccess.PageAccess_id id,Name  FROM mc_rolepageaccess 
                JOIN h_pageaccess ON h_pageaccess.id=mc_rolepageaccess.PageAccess_id  WHERE mc_rolepageaccess.RoleAccess_id=%s ''',[id])
                RolePageAccessSerializer = MC_RolePageAccessSerializer(RolePageAccess,  many=True).data
                Pagesdata.append( {
                    "id": a1['Pages_id'],
                    "Name": a1['Name'],
                    "DisplayIndex": a1['DisplayIndex'],
                    "Icon": a1['Icon'],
                    "ActualPagePath": a1['ActualPagePath'],
                    "isShowOnMenu": a1['isShowOnMenu'], 
                    "RolePageAccess" :RolePageAccessSerializer
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
                RoleAccessSerialize_data = M_RoleAccessSerializer(data=RoleAccessdata,many=True)
                if RoleAccessSerialize_data.is_valid():
                    # return JsonResponse({'Data':RoleAccessSerialize_data.data[0]['Role']})
                    RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                    RoleAccessdata.delete()
                    RoleAccessSerialize_data.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Access Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class RoleAccessViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    
    def get(self, request,Role=0,Division=0,Company=0):
    
        modules = M_RoleAccess.objects.raw(
            '''SELECT distinct Modules_id id ,h_modules.id, h_modules.Name,h_modules.DisplayIndex 
FROM m_roleaccess 
join h_modules on h_modules.id=m_roleaccess.Modules_id
where Role_id =%s AND M_RoleAccess.Division_id=%s AND M_RoleAccess.Company_id=%s
ORDER BY h_modules.DisplayIndex''',([Role],[Division],[Company]))
        data = M_RoleAccessSerializerfordistinctModule(modules, many=True).data
        Moduledata = list()
        for a in data:
            id=a['id']
            query=M_RoleAccess.objects.raw('''SELECT m_roleaccess.id,m_pages.Name,m_pages.Description,m_pages.ActualPagePath,m_pages.DisplayIndex,
m_pages.Icon,m_pages.isActive,m_pages.isShowOnMenu,m_pages.Module_id,
m_pages.PageType,m_pages.RelatedPageID, 
Pages_id FROM erpdatabase.m_roleaccess
JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id 
WHERE Role_id=%s AND  Modules_id=%s ''',([Role],[id]))

           
            PageSerializer = M_PagesSerializerforRoleAccessNEW(query,  many=True).data
            Pagesdata = list()
            for a1 in PageSerializer:
                id=a1['id']
                RolePageAccess=MC_RolePageAccess.objects.raw(''' SELECT mc_rolepageaccess.PageAccess_id id,Name  FROM mc_rolepageaccess 
                JOIN h_pageaccess ON h_pageaccess.id=mc_rolepageaccess.PageAccess_id  WHERE mc_rolepageaccess.RoleAccess_id=%s ''',[id])
                RolePageAccessSerializer = MC_RolePageAccessSerializer(RolePageAccess,  many=True).data
                Pagesdata.append( {
                    "id": a1['Pages_id'],
                    "Name": a1['Name'],
                    "DisplayIndex": a1['DisplayIndex'],
                    "Icon": a1['Icon'],
                    "ActualPagePath": a1['ActualPagePath'],
                    "isShowOnMenu": a1['isShowOnMenu'], 
                    "RolePageAccess" :RolePageAccessSerializer
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
    
    
class RoleAccessViewList(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self,request,id=0):
            try:
                with transaction.atomic():
                    query= M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id,M_Roles.Name RoleName,M_DivisionType.Name DivisionName,C_Companies.Name CompanyName
    FROM M_RoleAccess
    join M_Roles ON M_Roles.id=M_RoleAccess.Role_id
    join M_DivisionType  ON M_DivisionType.id=M_RoleAccess.Division_id
    join C_Companies  ON C_Companies.id=M_RoleAccess.Company_id group by Role_id,Company_id,Division_id''')
                    if not query:
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data':[]})
                    else:
                        M_Items_Serializer = M_RoleAccessSerializerGETList(query, many=True).data
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Items_Serializer})
                        
            except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                RoleAccessdata = M_RoleAccess.objects.get(id=id)
                RoleAccessdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'RoleAccess  Deleted Successfully', 'Data':[]})
        except M_RoleAccess.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'RoleAccess Not available', 'Data': []})        

                              