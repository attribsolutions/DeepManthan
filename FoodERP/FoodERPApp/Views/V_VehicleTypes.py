from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_VehicleTypes import *

from ..models import *


class M_VehicleTypesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                VehicleTypedata = JSONParser().parse(request)
                VehicleTypedata = M_VehicleTypes.objects.filter(Company=1)
                if VehicleTypedata.exists():
                    VehicleType_Serializer = VehicleTypesSerializer(VehicleTypedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': VehicleType_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Vehicle Type Not Available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   

class M_VehicleTypesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    
    
    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                VehicleTypedata = JSONParser().parse(request)
                VehicleType_Serializer = VehicleTypesSerializer(data=VehicleTypedata)
            if VehicleType_Serializer.is_valid():
                VehicleType_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Type Save Successfully', 'Data': []})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': VehicleType_Serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse(
                {'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                VehicleTypedata = M_VehicleTypes.objects.get(id=id)
                VehicleType_Serializer = VehicleTypesSerializer(VehicleTypedata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': VehicleType_Serializer.data})
        except  M_VehicleTypes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Vehicle Type Not available', 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                VehicleTypedata = JSONParser().parse(request)
                VehicleTypedataByID = M_VehicleTypes.objects.get(id=id)
                VehicleType_Serializer = VehicleTypesSerializer(
                    VehicleTypedataByID, data=VehicleTypedata)
                if VehicleType_Serializer.is_valid():
                    VehicleType_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Type Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': VehicleType_Serializer.errors, 'Data' :[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Executiono Error', 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                VehicleTypedata = M_VehicleTypes.objects.get(id=id)
                VehicleTypedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Type Deleted Successfully','Data':[]})
        except M_VehicleTypes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Vehicle Type Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message':'Vehicle Type used in another table', 'Data': []})