from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser


from ..Serializer.S_GeneralMaster import *

from ..models import C_Companies

class GeneralMasterFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GeneralMasterdata = JSONParser().parse(request)
                Type = GeneralMasterdata['Type']
                CompanyID = GeneralMasterdata['Company']
                if Type !='':
                    query = M_GeneralMaster.objects.filter(Company=CompanyID,Type=Type)
                else:    
                    query = M_GeneralMaster.objects.filter(Company=CompanyID)
                if query:
                    GeneralMaster_Serializer = GeneralMasterserializer(query, many=True).data
                    GeneralMaster_SerializerList = list()
                    for a in GeneralMaster_Serializer:   
                        GeneralMaster_SerializerList.append({
                        "id": a['id'],
                        "Type": a['Type'],
                        "Name": a['Name'],
                        "IsActive": a['IsActive'],
                        "Flag":a['Flag'],
                        "Company": a['Company']['id'],
                        "CompanyName":a['Company']['Name'],
                        }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_SerializerList})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
            
            
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
                    "id": a['id'],
                    "Type": a['Type'],
                    })
                GeneralMaster_SerializerList.append({"Type":"NewGeneralMasterType"})     
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_SerializerList})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})              
    
    

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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GenearlMaster Save Successfully', 'Data':[]})
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
                            "Type": a['Type'],
                            "Name": a['Name'],
                            "IsActive": a['IsActive'],
                            "Flag": a['Flag']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GeneralMasterList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                CompaniesdataByID = C_Companies.objects.get(id=id)
                Companies_Serializer = GeneralMasterserializer(
                    CompaniesdataByID, data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(id=id)
                Companiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Deleted Successfully', 'Data':[]})
        except C_Companies.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company used in another table', 'Data': []})   