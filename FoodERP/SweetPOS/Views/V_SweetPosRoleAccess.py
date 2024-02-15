from FoodERPApp.models import DBNameFun
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
                    if 'Division' in data and M_SweetPOSRoleAccess.objects.filter(Division=data['Division']).exists():
                        # Object exists, update it\
                        
                        obj = M_SweetPOSRoleAccess.objects.get(Division=data['Division'])
                        
                        for key, value in data.items():
                           setattr(obj, key, value)
                        obj.save()
                        
                    else:
                        obj = M_SweetPOSRoleAccess(**data)
                        obj.save()
                        # return obj
                    
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SweetPosRoleAccess Save Successfully', 'Data':[]}) 
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  list(e), 'Data':[]})
        
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                # Get a cursor object
                # with connection.cursor() as cursor:
                #     raw_query = "SELECT 1 id,DBNameFun('default')DB "
                #     cursor.execute(raw_query)
                #     results = cursor.fetchall()
                #     for result in results:
                #         print(result,result[1])
                RoleAccessData = M_SweetPOSRoleAccess.objects.raw('''Select A.id, A.Name,A.id Party, B.*
                                        From devfooderp20240214.M_Parties A
                                        Left Join sweetpos.M_SweetPOSRoleAccess B on A.id = B.Party
                                        where A.PartyType_id = 19''')
                print(RoleAccessData)                        
                RoleAccess_serializer = SPOSRoleAccessSerializerSecond(RoleAccessData, many=True).data
                # for a in RoleAccessData:
                #     print(a)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': RoleAccess_serializer})
        except  M_SweetPOSRoleAccess.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'RoleAccess Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



class SPOSLog_inView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        try:
            
            with transaction.atomic():
                SPOSLog_in_data = JSONParser().parse(request)
                DivisionID = SPOSLog_in_data['DivisionID']
                SPOSLog_in_data_serializer = SPOSLog_inSerializer(data=SPOSLog_in_data)
                if SPOSLog_in_data_serializer.is_valid():
                    SPOSLog_in_data_serializer.save()
                    
                    responce=M_SweetPOSRoleAccess.objects.get(Division=DivisionID)
                    responce_serializer=SPOSRoleAccessSerializer(responce).data

                    return JsonResponse({"Success":True,"status_code":200,"msg":"Loged In Successfully..!","RoleAccess": responce_serializer})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SPOSLog_in_data_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})