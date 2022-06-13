from dataclasses import field
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Pages import M_PagesSerializer, M_PagesSerializer1

from ..models import M_Pages

class M_PagesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):
        try:
            # time.sleep(7)
            with transaction.atomic():
                HPagesdata = M_Pages.objects.raw('''SELECT p.ID,p.Name,p.Description,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,RP.ID RelatedPageID,
Rp.Name RelatedPageName 
FROM M_Pages p 
join H_Modules m on p.Module_id= m.ID
left join M_Pages RP on p.RelatedPageID=RP.id ''')
                
                # if HPagesdata.exists():
                HPagesserialize_data = M_PagesSerializer(HPagesdata, many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': HPagesserialize_data})
                # return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})
        except Exception as e:
            raise Exception(e)



    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                HPagesdata = JSONParser().parse(request)
                HPagesserialize_data = M_PagesSerializer1(data=HPagesdata)
                if HPagesserialize_data.is_valid():
                    HPagesserialize_data.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Page Save Successfully'})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': HPagesserialize_data.errors})
        except Exception as e:
            raise Exception(e)


class M_PagesViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                HPagesdata = M_Pages.objects.raw('''SELECT p.ID,p.Name,p.Description,p.isActive,p.DisplayIndex,p.Icon,p.ActualPagePath,
m.ID ModuleID,m.Name ModuleName,RP.ID RelatedPageID,
Rp.Name RelatedPageName 
FROM M_Pages p 
join H_Modules m on p.Module_id= m.ID
left join M_Pages RP on p.RelatedPageID=RP.id where p.ID= %s''', [id])
                # if HPagesdata.exists():
                HPagesserialize_data = M_PagesSerializer(HPagesdata, many=True).data
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': HPagesserialize_data})
                # return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})    
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = M_Pages.objects.get(ID=id)
                Modulesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' H_Pages Deleted Successfully'})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = JSONParser().parse(request)
                ModulesdataByID = M_Pages.objects.get(ID=id)
                Modules_Serializer = M_PagesSerializer1(
                    ModulesdataByID, data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'H_Pages Updated Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Modules_Serializer.errors})
        except Exception as e:
            raise Exception(e)
            print(e)

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
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':HPageListData})
        except Exception as e:
            raise Exception(e)
            print(e)            