from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Vehicles import *

from ..models import *


class M_VehicleView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_Vehicles.objects.raw(
                    '''SELECT m_vehicles.id, m_vehicles.VehicleNumber, m_vehicles.Description, m_drivers.Name DriverName,m_vehicletypes.Name Vehicletype FROM  m_vehicles JOIN  m_drivers ON m_drivers.id = m_vehicles.Driver_id JOIN  m_vehicletypes ON m_vehicletypes.id = m_vehicles.VehicleType_id ''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Vehicle Not available', 'Data': []})
                else:
                    Vehicles_Serializer = M_VehiclesSerializerList(
                        query, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Vehicles_Serializer.data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Vehiclesdata = JSONParser().parse(request)
                Vehicles_Serializer = M_VehiclesSerializer(data=Vehiclesdata)
            if Vehicles_Serializer.is_valid():
                Vehicles_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Save Successfully', 'Data': []})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Vehicles_Serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse(
                {'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


class M_VehicleViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Vehicle = M_Vehicles.objects.filter(id=id)
                Vehicle_serializer = VehiclesSerializerSecond(
                    Vehicle, many=True).data
                VehicleData = list()
                for a in Vehicle_serializer:
                    Divisions = list()
                    for b in a['VehicleDivisions']:
                        Divisions.append({
                        "Division": b['Division']['id'],
                        "DivisionName": b['Division']['Name'],

                        })
                    VehicleData.append({
                        "id": a['id'],
                        "VehicleNumber": a['VehicleNumber'],
                        "Description": a['Description'],
                        "Driver": a['Driver']['id'],
                        "DriverName": a['Driver']['Name'],
                        "VehicleType": a['VehicleType']['id'],
                        "VehicleTypeName": a['VehicleType']['Name'],
                        "VehicleDivisions": Divisions,
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "UpdatedBy": a['UpdatedBy'],
                        "UpdatedOn": a['UpdatedOn']
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': VehicleData[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Vehiclesdata = JSONParser().parse(request)
                VehiclesdataByID = M_Vehicles.objects.get(id=id)
                Vehicle_Serializer = M_VehiclesSerializer(
                    VehiclesdataByID, data=Vehiclesdata)
                if Vehicle_Serializer.is_valid():
                    Vehicle_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': Vehicle_Serializer.errors,'Data' :[]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' Exception Found','Data' :[]})
    
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Vehiclesdata = M_Vehicles.objects.get(id=id)
                Vehiclesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Deleted Successfully','Data':[]})
        except M_Vehicles.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Vehicle Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message':'Vehicle used in another table', 'Data': []}) 
