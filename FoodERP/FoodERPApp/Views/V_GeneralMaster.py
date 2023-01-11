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
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = C_Companies.objects.all()
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = GeneralMasterserializer(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]}) 




class GeneralMasterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
                   
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = C_Companies.objects.all()
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = GeneralMasterserializer(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})                

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                Companies_Serializer = C_CompanySerializer(data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
            


class GeneralMasterViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = C_Companies.objects.filter(id=id)
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = GeneralMasterserializer(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                CompaniesdataByID = C_Companies.objects.get(id=id)
                Companies_Serializer = C_CompanySerializer(
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