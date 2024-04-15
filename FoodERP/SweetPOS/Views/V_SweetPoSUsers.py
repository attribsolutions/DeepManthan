import base64
from ..models import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
from FoodERPApp.models import *
from ..Serializer.S_SweetPoSUsers import *
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew



class SweetPOSUsersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        User_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                User_data_serializer  = UsersSerializer(data=User_data )
                if User_data_serializer .is_valid():
                    User_data_serializer .save()
                    log_entry = create_transaction_logNew(request, User_data,0,'',372,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Data Uploaded Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, User_data,0,'UserSave:'+str(User_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': User_data_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, User_data, 0,'UserSave:'+str(e),33,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                User_data = M_SweetPOSUser.objects.all()
                User_data_serializer = UsersSerializer(User_data,many=True)
                # log_entry = create_transaction_logNew(request, User_data,0,'',373,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': User_data_serializer.data})
        except  M_SweetPOSUser.DoesNotExist:
            # log_entry = create_transaction_logNew(request,0,0,'Users Data Does Not Exist',373,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Users Data Not available', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETAllUsers:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
    
class SweetPOSUsersSecondView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                User_data = M_SweetPOSUser.objects.get(id=id)
                User_data_serializer = UsersSerializer(User_data)
                log_entry = create_transaction_logNew(request, User_data,0,'',374,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': User_data_serializer.data})
        except  M_SweetPOSUser.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'User Data Does Not Exist',374,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'User Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETSingleUser:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        


    @transaction.atomic()
    def put(self, request, id=0):
        User_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                User_DataByID  = M_SweetPOSUser.objects.get(id=id)
                User_data_serializer = UsersSerializer(User_DataByID , data=User_data)
                if User_data_serializer.is_valid():
                    User_data_serializer.save()
                    log_entry = create_transaction_logNew(request, User_data,0,'',375,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Data Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, User_data,0,'UserEdit:'+str(User_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': User_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, User_data, 0,'UserEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                User_data = M_SweetPOSUser.objects.get(id=id)
                User_data.delete()
                log_entry = create_transaction_logNew(request, User_data,0,'',376,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Data Deleted Successfully','Data':[]})
        except M_SweetPOSUser.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'User Data Not available',376,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'User Data Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'User Data used in another table',8,0)  
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'User Data used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'UserDelete:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})  


class SweetPOSRolesView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                role_data = M_SweetPOSRoles.objects.all()
                role_data_serializer = RolesSerializer(role_data,many=True).data
                # log_entry = create_transaction_logNew(request, role_data,0,'',377,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': role_data_serializer})
        except  M_SweetPOSRoles.DoesNotExist:
            # log_entry = create_transaction_logNew(request,0,0,'Role Data Does Not Exist',377,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Role Not available', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETAllRoles:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})  