from django.http import JsonResponse
from rest_framework.response import Response

from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_RoleAccess import *
from ..models import *


class RoleAccessClass(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):

        modules = M_RoleAccess.objects.raw(
            '''SELECT distinct Modules_id id ,h_modules.id, h_modules.Name,h_modules.DisplayIndex 
FROM m_roleaccess 
join h_modules on h_modules.id=m_roleaccess.Modules_id
ORDER BY h_modules.DisplayIndex''')
        data = M_RoleAccessSerializerfordistinctModule(modules, many=True).data

        Moduledata = list()

        for a in data:

            people1 = M_RoleAccess.objects.filter(
                Role=1).filter(Modules=a['id']).values("Pages")
            Pages = M_Pages.objects.filter(isActive=1).filter(id__in=people1)
            Pagesfields = ('id', 'Name', 'DisplayIndex', 'Icon',
                           'ActualPagePath', 'isShowOnMenu')
            PageSerializer = M_PagesSerializerforRoleAccess(
                Pages,  many=True, fields=Pagesfields).data
            Pagesdata = list()
            for a1 in PageSerializer:

                Pagesdata.append(a1)

            response1 = {
                "ModuleID": a['id'],
                "ModuleName": a['Name'],
                "ModuleData": Pagesdata,
                # "query":str(Pages.query)
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

   