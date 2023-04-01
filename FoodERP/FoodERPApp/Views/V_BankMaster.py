from ..models import *
from ..Serializer.S_BankMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

class BankListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request,id=0):
        try:
            with transaction.atomic():
                Bank_data = JSONParser().parse(request)
                Party = Bank_data['Party']
                Company = Bank_data['Company']
                query = M_Bank.objects.filter(Party=Party, Company=Company)
        
                if query:
                    bank_serializer = BankSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :bank_serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
class BankView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request):
        try:
            with transaction.atomic():
                Bank_data = JSONParser().parse(request)
                Bank_serializer = BankSerializer(data=Bank_data)
            if Bank_serializer.is_valid():
                Bank_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Save Successfully', 'Data' :[]})
            else :
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Bank_serializer.errors, 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Bankdata = M_Bank.objects.get(id=id)
                Bank_serializer = BankSerializer(Bankdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Bank_serializer.data})
        except  M_Bank.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Bank Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Bankdata = JSONParser().parse(request)
                BankdataByID = M_Bank.objects.get(id=id)
                Bank_serializer = BankSerializer(
                    BankdataByID, data=Bankdata)
                if Bank_serializer.is_valid():
                    Bank_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Bank_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Bankdata = M_Bank.objects.get(id=id)
                Bankdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Deleted Successfully','Data':[]})
        except M_Bank.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bank Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bank used in transaction', 'Data': []})
            
            




                








        