from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Vehicles import *
from ..models import *
from ..Serializer.S_Orders import *

class VehicleViewList(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Vehicledata = JSONParser().parse(request)
                Company = Vehicledata['CompanyID']
                Party = Vehicledata['PartyID']
                VehicleNamedata = M_Vehicles.objects.filter(Party=Party,Company=Company)
                if VehicleNamedata.exists():
                    Vehicle_Serializer = VehiclesSerializerSecond(VehicleNamedata, many=True).data
                    VehicleData = list()
                    for a in Vehicle_Serializer:
                        VehicleData.append({
                            "id": a['id'],
                            "VehicleNumber": a['VehicleNumber'],
                            "Party": a['Party'],
                            "Company": a['Company'],
                            "Description": a['Description'],
                            "VehicleType": a['VehicleType']['id'],
                            "VehicleTypeName": a['VehicleType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })

                    log_entry = create_transaction_logNew(request, Vehicledata,Party,"Vehicle List",147,0,0,0,Company)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': VehicleData})
                log_entry = create_transaction_logNew(request, Vehicledata,0,"Data Not Available",7,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Vehicle Not Available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Vehicledata,0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class VehicleView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Vehiclesdata = JSONParser().parse(request)
                Vehicles_Serializer = VehiclesSerializer(data=Vehiclesdata)
            if Vehicles_Serializer.is_valid():
                Vehicle = Vehicles_Serializer.save()
                LastInsertId = Vehicle.id
                log_entry = create_transaction_logNew(request, Vehiclesdata,Vehiclesdata['Party'],"Vehicle Save Successfully",13,LastInsertId,0,0,Vehiclesdata['Company'])
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Save Successfully', 'TransactionID': LastInsertId, 'Data': []})
            else:
                log_entry = create_transaction_logNew(request, Vehiclesdata,0,Vehicles_Serializer.errors,34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Vehicles_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Vehiclesdata,0,str(e),33,0)
            raise JsonResponse(
                {'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Vehicle = M_Vehicles.objects.filter(id=id)
                Vehicle_serializer = VehiclesSerializerSecond(Vehicle, many=True).data
                VehicleData = list()
                for a in Vehicle_serializer:
                    VehicleData.append({
                        "id": a['id'],
                        "VehicleNumber": a['VehicleNumber'],
                        "Party": a['Party'],
                        "Company": a['Company'],
                        "Description": a['Description'],
                        "VehicleType": a['VehicleType']['id'],
                        "VehicleTypeName": a['VehicleType']['Name'],
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "UpdatedBy": a['UpdatedBy'],
                        "UpdatedOn": a['UpdatedOn']
                    })
                
                log_entry = create_transaction_logNew(request, Vehicle_serializer,a['Party'],"Single Vehicle",148,0,0,0, a['Company'])
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': VehicleData[0]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Vehicle_serializer,0,str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Vehiclesdata = JSONParser().parse(request)
                VehiclesdataByID = M_Vehicles.objects.get(id=id)
                Vehicle_Serializer = VehiclesSerializer(
                    VehiclesdataByID, data=Vehiclesdata)
                if Vehicle_Serializer.is_valid():
                    Vehicle_Serializer.save()
                    log_entry = create_transaction_logNew(request, Vehiclesdata,Vehiclesdata['Party'],"Vehicle Updated Successfully",14,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Updated Successfully','Data' : []})
                else:
                    log_entry = create_transaction_logNew(request, Vehiclesdata,0,Vehicle_Serializer.errors,34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': Vehicle_Serializer.errors,'Data' :[]})
        except Exception :
            log_entry = create_transaction_logNew(request, Vehiclesdata,0,"Exception Found",33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' Exception Found','Data' :[]})
    
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Vehiclesdata = M_Vehicles.objects.get(id=id)
                Vehiclesdata.delete()
                log_entry = create_transaction_logNew(request, {'VehicleId':id},0,"Vehicle Deleted Successfully",15,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Vehicle Deleted Successfully','Data':[]})
        except M_Vehicles.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,"Vehicle Not available",7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Vehicle Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request, 0,0,"Vehicle used in another table",8,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message':'Vehicle used in another table', 'Data': []}) 
