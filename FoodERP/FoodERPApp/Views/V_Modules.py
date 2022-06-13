
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Modules import *

from ..models import *


class H_ModulesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.all()
                if Modulesdata.exists():
                    Modules_Serializer = H_ModulesSerializer(
                    Modulesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data })
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})    
        except Exception as e:
            raise Exception(e)
            
            print(e)


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Modulesdata = JSONParser().parse(request)
                Modules_Serializer = H_ModulesSerializer(data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Save Successfully','Data' :''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Modules_Serializer.errors,'Data': ''})
        except Exception as e:
            raise Exception(e)
            print(e)        

class H_ModulesViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.filter(ID=id)
                if Modulesdata.exists():
                    Modules_Serializer = H_ModulesSerializer(Modulesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data})
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': ''})    
        except Exception as e:
            raise Exception(e)
            
            print(e)

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = H_Modules.objects.get(ID=id)
                Modulesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Deleted Successfully','Data' : ''})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Modulesdata = JSONParser().parse(request)
                ModulesdataByID = H_Modules.objects.get(ID=id)
               
                Modules_Serializer = H_ModulesSerializer(ModulesdataByID, data=Modulesdata)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Updated Successfully','Data':''})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Modules_Serializer.errors,'Data' :''})
                
        except Exception as e:
            raise Exception(e)
            print(e)            


            # H_Module input JSON
                # {     
                # "Name": "admin module1",
                # "DisplayIndex": 4,
                # "IsActive": true,
                # "Icon": "aaaabbb2"
                # }

# class H_SubModulesView(CreateAPIView):
    
#     permission_classes = (IsAuthenticated,)
#     authentication_class = JSONWebTokenAuthentication

#     def get(self, request):
#         try:
#             with transaction.atomic():
#                 SubmoduleListData=list()
#                 Submodule_data = H_SubModules.objects.all()
#                 Submoule_serializer_data = H_SubModulesSerializer(Submodule_data,many=True).data
                
#                 for a in Submoule_serializer_data:
#                     SubmoduleListData.append({
#                     'ID':a["ID"],
#                     'Name':a["Name"],
#                     'Icon':a["Icon"],
#                     'DisplayIndex':a["DisplayIndex"],  
#                     'ModuleID':a["Module"]['ID'], 
#                     'ModuleName':a["Module"]['Name'],
#                     'IsActive':a["IsActive"]
#                     })  

#                 return JsonResponse({'StatusCode': 200, 'Status': True,'Data': SubmoduleListData})
#         except Exception as e:
#             raise Exception(e)

#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 userdata = JSONParser().parse(request)
#                 H_SubModules_Serializer = H_SubModulesSerializer(data=userdata)
#                 if H_SubModules_Serializer.is_valid():
#                     H_SubModules_Serializer.save()
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubModules Save Successfully'})
#                 return JsonResponse({'StatusCode': 200, 'Status': True, 'data': H_SubModules_Serializer.errors})
#         except Exception as e:
#             raise Exception(e)


# class H_SubModulesViewSecond(RetrieveAPIView):

#     permission_classes = (IsAuthenticated,)
#     authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def get(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 SubmoduleListData=list()
#                 Submodule_data = H_SubModules.objects.get(ID=id)
#                 Submoule_serializer_data = H_SubModulesSerializer(Submodule_data).data
                
#                 for a in Submoule_serializer_data:
#                     SubmoduleListData.append({
#                     'ID':a["ID"],
#                     'Name':a["Name"],
#                     'Icon':a["Icon"],
#                     'DisplayIndex':a["DisplayIndex"],  
#                     'ModuleID':a["Module"]['ID'], 
#                     'ModuleName':a["Module"]['Name'],
#                     'IsActive':a["IsActive"]
#                     })  

#                 return JsonResponse({'StatusCode': 200, 'Status': True,'Data': SubmoduleListData})
#         except Exception as e:
#             raise Exception(e)

#     @transaction.atomic()
#     def delete(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Modulesdata = H_SubModules.objects.get(ID=id)
#                 Modulesdata.delete()
#                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubModule Deleted Successfully'})
#         except Exception as e:
#             raise Exception(e)
#             print(e)

#     @transaction.atomic()
#     def put(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Modulesdata = JSONParser().parse(request)
#                 ModulesdataByID = H_SubModules.objects.get(ID=id)
#                 Modules_Serializer = H_SubModulesSerializer(
#                     ModulesdataByID, data=Modulesdata)
#                 if Modules_Serializer.is_valid():
#                     Modules_Serializer.save()
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Updated Successfully'})
#                 else:
#                     transaction.set_rollback(True)
#                     return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Modules_Serializer.errors})
#         except Exception as e:
#             raise Exception(e)
#             print(e)                