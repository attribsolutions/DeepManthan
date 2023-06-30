from ..models import *
from ..Serializer.S_BankMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

class PartyBanksFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request,id=0):
        try:
            with transaction.atomic():
                Bank_data = JSONParser().parse(request)
                Party = Bank_data['PartyID']
                Company = Bank_data['CompanyID']
                query1 = MC_PartyBanks.objects.raw('''SELECT MC_PartyBanks.id, M_Bank.id AS Bank_id, MC_PartyBanks.IFSC, MC_PartyBanks.BranchName, MC_PartyBanks.AccountNo, MC_PartyBanks.CustomerBank, MC_PartyBanks.IsSelfDepositoryBank, MC_PartyBanks.Company_id, MC_PartyBanks.Party_id, MC_PartyBanks.IsDefault FROM M_Bank LEFT JOIN MC_PartyBanks ON MC_PartyBanks.Bank_id = M_Bank.id AND MC_PartyBanks.Party_id=%s ORDER BY MC_PartyBanks.Party_id desc''',([Party]))
              
                if query1:
                    bank_serializer = PartyBanksSerializer(query1, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :bank_serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class PartyBanksListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request,id=0):
        try:
            with transaction.atomic():
                Bank_data = JSONParser().parse(request)
                Party = Bank_data['PartyID']
                Company = Bank_data['CompanyID']
                query = MC_PartyBanks.objects.filter(Party=Party, Company=Company)
                if query:
                    bank_serializer = PartyBanksSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :bank_serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class PartyBanksSaveView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PartyBanks_data = JSONParser().parse(request)
                PartyBanks_serializer = PartyBanksSerializerSecond(data=PartyBanks_data, many=True)
                if PartyBanks_serializer.is_valid():
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': PartyBanks_serializer.data})
                    id = PartyBanks_serializer.data[0]['Party']
                    MC_PartyBanks_data = MC_PartyBanks.objects.filter(Party=id)
                    MC_PartyBanks_data.delete()
                    PartyBanks_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Banks Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyBanks_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class BankListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request):
        try:
            with transaction.atomic():
                query = M_Bank.objects.all()
                if query:
                    bank_serializer = BankSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :bank_serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class BankView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Bank_data = JSONParser().parse(request)
                Bank_serializer = BankSerializer(data=Bank_data)
                if Bank_serializer.is_valid():
                    Bank_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Bank_serializer.errors, 'Data':[]})
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
            
            




                








        