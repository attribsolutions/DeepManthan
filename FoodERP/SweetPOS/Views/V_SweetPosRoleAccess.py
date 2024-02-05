from ..models import *
from ..Serializer.S_SweetPosRoleAccess import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
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
                RoleAccess_serializer = SPOSRoleAccessSerializer(data=SPOSRoleAccessdata)

                if RoleAccess_serializer.is_valid():
                    SPOSRoleAccessData = RoleAccess_serializer.save()
                    SPOSRoleAccessData.save(using='sweetpos_db')
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SeewtPosRoleAccess Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  RoleAccess_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                RoleAccessData = M_SweetPOSRoleAccess.objects.raw('''Select A.id, A.Name, B.*
                                        From devfooderp20240103.M_Parties A
                                        Left Join sweetpos.M_SweetPOSRoleAccess B on A.id = B.Division
                                        where A.PartyType_id = 19''')
                RoleAccess_serializer = SPOSRoleAccessSerializerSecond(RoleAccessData, many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': RoleAccess_serializer})
        except  M_SweetPOSRoleAccess.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'RoleAccess Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class SPosRoleAccessUpdateView(CreateAPIView):        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                SPOSRoleAccessdata = JSONParser().parse(request)
                SPOSRoleAccessByID = M_SweetPOSRoleAccess.objects.get(id=id)
                SPOSRoleAccess_serializer = SPOSRoleAccessSerializer(SPOSRoleAccessByID, data=SPOSRoleAccessdata)
                if SPOSRoleAccess_serializer.is_valid():
                    SPOSRoleAccessData = SPOSRoleAccess_serializer.save()
                    SPOSRoleAccessData.save(using='sweetpos_db')
                    # SPOSRoleAccess_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SPOSRoleAccess Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SPOSRoleAccess_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
