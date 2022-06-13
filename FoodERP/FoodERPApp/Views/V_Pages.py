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
                PageListData = list()
                HPagesdata = M_Pages.objects.all()
                HPagesserialize_data = M_PagesSerializer(HPagesdata, many=True).data
                
                for a1 in HPagesserialize_data:
                       PageListData.append({
                       'ID':a1["ID"],
                       'Name':a1["Name"],
                       'Icon':a1["Icon"],
                       'DisplayIndex':a1["DisplayIndex"],  
                       'ModuleID':a1["Module"]['ID'], 
                       'ModuleName':a1["Module"]['Name'],
                    #    'SubModuleID':a1["SubModule"]['ID'], 
                    #    'SubModuleName':a1["SubModule"]['Name'],
                       'Description':a1["Description"],
                       'ActualPagePath':a1["ActualPagePath"],
                       'IsActive':a1["isActive"],
                       'isShowOnMenu':a1["isShowOnMenu"],
                       'PageType':a1["PageType"],
                       'RelatedPageID' : a1["RelatedPageID"],

                        })
                # PageListData.append(response1)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': PageListData})
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
                PageListData = list()
                HPagesdata = M_Pages.objects.get(ID=id)
                HPagesserialize_data = M_PagesSerializer(HPagesdata).data
                PageListData.append({
                'ID':HPagesserialize_data["ID"],
                'Name':HPagesserialize_data["Name"],
                'Icon':HPagesserialize_data["Icon"],
                'DisplayIndex':HPagesserialize_data["DisplayIndex"],  
                'ModuleID':HPagesserialize_data["Module"]['ID'], 
                'ModuleName':HPagesserialize_data["Module"]['Name'],
                'Description':HPagesserialize_data["Description"],
                'ActualPagePath':HPagesserialize_data["ActualPagePath"],
                'IsActive':HPagesserialize_data["isActive"],
                'isShowOnMenu':HPagesserialize_data["isShowOnMenu"],
                'PageType':HPagesserialize_data["PageType"],
                'RelatedPageID' : HPagesserialize_data["RelatedPageID"],
                })  
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': PageListData})
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