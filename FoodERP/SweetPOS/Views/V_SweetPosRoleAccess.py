from ..models import *
from ..Serializer.S_SweetPosRoleAccess import *
from django.http import JsonResponse

from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

class SweetPosRoleAccessView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                SPOSRoleAccessdata = JSONParser().parse(request)
                response_data = []
                for data in SPOSRoleAccessdata:
                    RoleAccess_serializer = SPOSRoleAccessSerializer(data=data)
                    if RoleAccess_serializer.is_valid():
                        SPOSRoleAccessData = RoleAccess_serializer.save()
                        SPOSRoleAccessData.save(using='sweetpos_db')
                        # response_data.append(RoleAccess_serializer.data)
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  RoleAccess_serializer.errors, 'Data':[]})
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SeewtPosRoleAccess Save Successfully', 'Data':response_data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                RoleAccessData = M_SweetPOSRoleAccess.objects.raw('''Select A.id, A.Name, B.*
                                        From devfooderp20240123.M_Parties A
                                        Left Join sweetpos.M_SweetPOSRoleAccess B on A.id = B.Division
                                        where A.PartyType_id = 19''')
                RoleAccess_serializer = SPOSRoleAccessSerializerSecond(RoleAccessData, many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': RoleAccess_serializer})
        except  M_SweetPOSRoleAccess.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'RoleAccess Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class SPosRoleAccessUpdateView(RetrieveAPIView): 
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                SPOSRoleAccessData= JSONParser().parse(request)
                RoleAccessByID = M_SweetPOSRoleAccess.objects.using('sweetpos_db').get(Division=id)
                RoleAccess_Serializer = SPOSRoleAccessSerializer(RoleAccessByID, data=SPOSRoleAccessData)
                if RoleAccess_Serializer.is_valid():
                    SPOSRoleAccessData = RoleAccess_Serializer.save()
                    SPOSRoleAccessData.save(using='sweetpos_db')
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SPOSRoleAccess Updated Successfully','Data' :[]})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': RoleAccess_Serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    

# class SPOSRoleAccessPUT(RetrieveAPIView):
#     @transaction.atomic()
#     def put(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Modulesdata = JSONParser().parse(request)    
    

#         except Exception as e:
#             log_entry = create_transaction_logNew(request,0, 0,'ModuleUpdate:'+str(Exception),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})