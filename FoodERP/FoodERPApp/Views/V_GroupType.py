from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GroupType import *
from ..models import *
from ..Views.V_CommFunction import *

class GroupTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                GroupType_data = M_GroupType.objects.all()
                if GroupType_data.exists():
                    GroupType_serializer = GroupTypeSerializer(GroupType_data, many=True)
                    log_entry = create_transaction_logNew(request,GroupType_serializer, 0,'',395,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GroupType_serializer.data})
                log_entry = create_transaction_logNew(request,GroupType_serializer, 0,'Group Type Not available',395,0)
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Group Type Not available', 'Data': []})
        except Exception :
            log_entry = create_transaction_logNew(request,0, 0,'List of all GroupTypes'+'Execution Error',135,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        GroupType_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GroupType_serializer = GroupTypeSerializer(data=GroupType_data)
            if GroupType_serializer.is_valid():
                GroupType_serializer.save()
                log_entry = create_transaction_logNew(request,GroupType_data, 0,'',396,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Type Save Successfully', 'Data' :[]})
            else:
                log_entry = create_transaction_logNew(request,GroupType_data, 0,'GroupType Save:'+str(GroupType_serializer.errors),34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': GroupType_serializer.errors, 'Data' : []})
        except Exception :
            log_entry = create_transaction_logNew(request,GroupType_data, 0,'GroupType Save:'+'Execution Error',135,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})


class GroupTypeViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                GroupTypedata = M_GroupType.objects.get(id=id)
                GroupType_serializer = GroupTypeSerializer(GroupTypedata)
                log_entry = create_transaction_logNew(request,GroupType_serializer, 0,'',397,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': GroupType_serializer.data})
        except  M_GroupType.DoesNotExist:
            log_entry = create_transaction_logNew(request,0, 0,'Group Type Not available',7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Group Type Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'Get single GroupType:'+'Execution Error',135,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        GroupTypedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GroupTypedataByID = M_GroupType.objects.get(id=id)
                GroupType_serializer = GroupTypeSerializer(GroupTypedataByID, data=GroupTypedata)
                if GroupType_serializer.is_valid():
                    GroupType_serializer.save()
                    log_entry = create_transaction_logNew(request,GroupTypedata, 0,'',398,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Type Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request,GroupTypedata, 0,'GroupType Update:'+str(GroupType_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': GroupType_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,GroupTypedata, 0,'GroupType Update:'+'Execution Error',135,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GroupType_data = M_GroupType.objects.get(id=id)
                GroupType_data.delete()
                log_entry = create_transaction_logNew(request,0, 0,"GroupTypeID:"+str(id),399,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Type Deleted Successfully','Data':[]})
        except M_GroupType.DoesNotExist:
            log_entry = create_transaction_logNew(request,0, 0,'Group Type Not available',7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group Type Not available', 'Data': []})
        except IntegrityError:  
            log_entry = create_transaction_logNew(request,0, 0,'Group Type used in another table',8,0) 
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group Type used in another table', 'Data': []})