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
                    Salesmandata_serialiazer = SalemanSerializer(Salesmanquery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Salesmandata_serialiazer})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Salesman Not available ', 'Data': []})
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
                Salesman_Serializer = SalemanSerializer(data=Salesman_data)
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
                    Salesmandata = SalemanSerializer(Salesmanquery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Salesmandata[0]})
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
                Salesmandata_Serializer = SalemanSerializer(SalesmandatadataByID, data=Salesmandata)
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



