from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Salesman import *
from ..models import *


class SalesmanListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                Salesmandata = JSONParser().parse(request)
                Company = Salesmandata['CompanyID']
                Party = Salesmandata['PartyID']
                Salesmanquery = M_Salesman.objects.filter(Party=Party,Company=Company)
                if Salesmanquery.exists():
                    Salesmandata_serialiazer = SalesmanSerializerSecond(Salesmanquery, many=True).data
                    SalesmanList = list()
                    for a in Salesmandata_serialiazer:
                        SalesmanRouteList =list()
                        for b in a['SalesmanRoute']:
                            SalesmanRouteList.append({
                                "Route":b['Route']['id'],
                                "Name":b['Route']['Name']
                            }) 
                        SalesmanList.append({
                            "id":a['id'],
                            "Name":a['Name'],
                            "MobileNo":a['MobileNo'],
                            "IsActive":a['IsActive'],
                            "CreatedBy":a['CreatedBy'],
                            "UpdatedBy":a['UpdatedBy'],
                            "Company":a['Company'],
                            "Party":a['Party'],
                            "SalesmanRoute":SalesmanRouteList,
                        })     
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': SalesmanList})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Salesman Not available', 'Data': []})
        except M_Salesman.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Salesman Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
     

class SalesmanView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Salesman_data = JSONParser().parse(request)
                Salesman_Serializer = SalesmanSerializer(data=Salesman_data)
                if Salesman_Serializer.is_valid():
                    Salesman_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Salesman Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Salesman_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Salesmanquery = M_Salesman.objects.filter(id=id)
                if Salesmanquery.exists():

                    Salesmandata_serialiazer = SalesmanSerializerSecond(Salesmanquery, many=True).data  
                    SalesmanList = list()
                    for a in Salesmandata_serialiazer:
                           SalesmanRoutelist = list()
                           for b in a['SalesmanRoute']:
                            SalesmanRoutelist.append({
                                "Route":b['Route']['id'],
                                "Name":b['Route']['Name']
                            })

                            SalesmanList.append({
                                "id":a['id'],
                                "Name":a['Name'],
                                "MobileNo":a['MobileNo'],
                                "IsActive":a['IsActive'],
                                "CreatedBy":a['CreatedBy'],
                                "UpdatedBy":a['UpdatedBy'],
                                "Company":a['Company'],
                                "Party":a['Party'],
                                "SalesmanRoute":SalesmanRoutelist
                            })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SalesmanList[0]})

                   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Salesman Not available ', 'Data': []})
        except M_Salesman.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Salesman Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Salesmandata = JSONParser().parse(request)
                SalesmandatadataByID = M_Salesman.objects.get(id=id)
                Salesmandata_Serializer = SalesmanSerializer(SalesmandatadataByID, data=Salesmandata)
                if Salesmandata_Serializer.is_valid():
                    Salesmandata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Salesman Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Salesmandata_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Salesmandata = M_Salesman.objects.get(id=id)
                Salesmandata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Salesman Deleted Successfully', 'Data':[]})
        except M_Salesman.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Salesman Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Salesman used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   



