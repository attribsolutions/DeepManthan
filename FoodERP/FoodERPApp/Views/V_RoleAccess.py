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

    def get(self, request):

        modules = M_RoleAccess.objects.raw(
            '''SELECT distinct Modules_id id ,h_modules.id, h_modules.Name,h_modules.DisplayIndex 
FROM m_roleaccess 
join h_modules on h_modules.id=m_roleaccess.Modules_id
where Role_id =1
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
                    "id": a1['id'],
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

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                RoleAccessdata = JSONParser().parse(request)
                RoleAccessSerialize_data = M_RoleAccessSerializer(
                    data=RoleAccessdata)
                if RoleAccessSerialize_data.is_valid():
                    RoleAccessSerialize_data.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Access Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class RoleAccessViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = JSONParser().parse(request)
                M_PartiesdataByID = M_Parties.objects.get(id=id)
                M_Parties_Serializer = M_RoleAccessSerializer(
                    M_PartiesdataByID, data=M_Partiesdata)
                if M_Parties_Serializer.is_valid():
                    M_Parties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e),'Data' : []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = M_Parties.objects.get(ID=id)
                M_Partiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party  Deleted Successfully', 'Data':[]})
        except M_Parties.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Not available', 'Data': []})    
               