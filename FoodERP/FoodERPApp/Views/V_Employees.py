
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Employees import *

from ..models import *


class M_EmployeesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                M_Employessdata = M_Employess.objects.all()
                if M_Employessdata.exists():
                    M_Employess_Serializer = M_EmployessSerializer(
                    M_Employessdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_Employess_Serializer.data })
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})    
        except Exception as e:
            raise Exception(e)
            
            print(e)


#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 Modulesdata = JSONParser().parse(request)
#                 Modules_Serializer = H_ModulesSerializer(data=Modulesdata)
#                 if Modules_Serializer.is_valid():
#                     Modules_Serializer.save()
                   
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Save Successfully','Data' :''})
#                 else:
#                     transaction.set_rollback(True)
#                     return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Modules_Serializer.errors,'Data': ''})
#         except Exception as e:
#             raise Exception(e)
#             print(e)        

# class H_ModulesViewSecond(RetrieveAPIView):
    
#     permission_classes = (IsAuthenticated,)
#     authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def get(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Modulesdata = H_Modules.objects.filter(ID=id)
#                 if Modulesdata.exists():
#                     Modules_Serializer = H_ModulesSerializer(Modulesdata, many=True)
#                     return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data})
#                 return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': ''})    
#         except Exception as e:
#             raise Exception(e)
            
#             print(e)

#     @transaction.atomic()
#     def delete(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Modulesdata = H_Modules.objects.get(ID=id)
#                 Modulesdata.delete()
#                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Deleted Successfully','Data' : ''})
#         except Exception as e:
#             raise Exception(e)
#             print(e)

#     @transaction.atomic()
#     def put(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Modulesdata = JSONParser().parse(request)
#                 ModulesdataByID = H_Modules.objects.get(ID=id)
               
#                 Modules_Serializer = H_ModulesSerializer(ModulesdataByID, data=Modulesdata)
#                 if Modules_Serializer.is_valid():
#                     Modules_Serializer.save()
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Module Updated Successfully','Data':''})
#                 else:
#                     transaction.set_rollback(True)
#                     return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Modules_Serializer.errors,'Data' :''})
                
#         except Exception as e:
#             raise Exception(e)
#             print(e)            
