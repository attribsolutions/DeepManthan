from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser


from ..Serializer.S_GeneralMaster import *

from ..models import C_Companies



#List API View

class GeneralMasterFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GeneralMasterdata = JSONParser().parse(request)
                Type = GeneralMasterdata['Type']
                Company = GeneralMasterdata['Company']
                if Type !='':
                    query = M_GeneralMaster.objects.filter(Company=Company,Type=Type)
                else:    
                    query = M_GeneralMaster.objects.filter(Company=Company)
                if query:
                    GeneralMaster_Serializer = GeneralMasterserializerSecond(query, many=True).data
                    GeneralMaster_SerializerList = list()
                    for a in GeneralMaster_Serializer:   
                        GeneralMaster_SerializerList.append({
                        "id": a['id'],
                        "TypeID": a['TypeID'],
                        "Name": a['Name'],
                        "IsActive": a['IsActive'],
                        "Company": a['Company']['id'],
                        "CompanyName":a['Company']['Name']
                        }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_SerializerList })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
            


#Get General Master Type -Post API             
class GeneralMasterTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GeneralMasterdata = JSONParser().parse(request)
                CompanyID = GeneralMasterdata['Company'] 
                query = M_GeneralMaster.objects.filter(Company=CompanyID)
                GeneralMaster_Serializer = GeneralMasterserializer(query, many=True).data
                GeneralMaster_SerializerList = list()
                for a in GeneralMaster_Serializer:   
                    GeneralMaster_SerializerList.append({
                    "id":a['id'],    
                    "TypeID": a['TypeID'],
                    "Name": a['Name']   
                    })
                GeneralMaster_SerializerList.append({"TypeID":"0","Name":"NewGeneralMasterType"})     
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_SerializerList})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})              
    
    
#Post API - Save API 
class GeneralMasterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication                      

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GeneralMasterdata = JSONParser().parse(request)
                GeneralMaster_Serializer = GeneralMasterserializer(data=GeneralMasterdata)
                if GeneralMaster_Serializer.is_valid():
                    GeneralMaster_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Genearl Master Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':GeneralMaster_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
            
class GeneralMasterViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = M_GeneralMaster.objects.filter(id=id)
                if query.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    GeneralMasterdata = GeneralMasterserializer(query, many=True).data
                    GeneralMasterList=list()
                    for a in GeneralMasterdata:
                        GeneralMasterList.append({
                            "id": a['id'],
                            "TypeID": a['TypeID'],
                            "Name": a['Name'],
                            "IsActive": a['IsActive']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GeneralMasterList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'General Master data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                GeneralMasterdata = JSONParser().parse(request)
                GeneralMasterdataByID = M_GeneralMaster.objects.get(id=id)
                GeneralMaster_Serializer = GeneralMasterserializer(
                    GeneralMasterdataByID, data=GeneralMasterdata)
                if GeneralMaster_Serializer.is_valid():
                    GeneralMaster_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'General Master Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': GeneralMaster_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GeneralMasterdata = M_GeneralMaster.objects.get(id=id)
                GeneralMasterdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'General Master Deleted Successfully', 'Data':[]})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'General Master used in another table', 'Data': []})   