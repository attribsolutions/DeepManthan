from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GroupType import *
from ..models import *

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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GroupType_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Group Type Not available', 'Data': []})
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GroupType_data = JSONParser().parse(request)
                GroupType_serializer = GroupTypeSerializer(data=GroupType_data)
            if GroupType_serializer.is_valid():
                GroupType_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Type Save Successfully', 'Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': GroupType_serializer.errors, 'Data' : []})
        except Exception :
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
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': GroupType_serializer.data})
        except  M_GroupType.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Group Type Not available', 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                GroupTypedata = JSONParser().parse(request)
                GroupTypedataByID = M_GroupType.objects.get(id=id)
                GroupType_serializer = GroupTypeSerializer(
                    GroupTypedataByID, data=GroupTypedata)
                if GroupType_serializer.is_valid():
                    GroupType_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Type Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': GroupType_serializer.errors, 'Data' :[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Executiono Error', 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GroupType_data = M_GroupType.objects.get(id=id)
                GroupType_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Type Deleted Successfully','Data':[]})
        except M_GroupType.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group Type Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group Type used in another table', 'Data': []})