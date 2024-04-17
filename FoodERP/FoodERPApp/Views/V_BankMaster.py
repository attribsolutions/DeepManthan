from ..models import *
from ..Serializer.S_BankMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from .V_CommFunction import *


class PartyBanksFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request,id=0):
        Bank_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = Bank_data['PartyID']
                Company = Bank_data['CompanyID']
                query1 = MC_PartyBanks.objects.raw('''SELECT MC_PartyBanks.id, M_Bank.id AS Bank_id, MC_PartyBanks.IFSC, MC_PartyBanks.BranchName, MC_PartyBanks.AccountNo, MC_PartyBanks.CustomerBank, MC_PartyBanks.IsSelfDepositoryBank, MC_PartyBanks.Company_id, MC_PartyBanks.Party_id, MC_PartyBanks.IsDefault FROM M_Bank LEFT JOIN MC_PartyBanks ON MC_PartyBanks.Bank_id = M_Bank.id AND MC_PartyBanks.Party_id=%s ORDER BY MC_PartyBanks.Party_id desc''',([Party]))
              
                if query1:
                    bank_serializer = PartyBanksSerializer(query1, many=True).data
                    log_entry = create_transaction_logNew(request, Bank_data,Party,'Company:'+str(Company),189,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :bank_serializer})
                log_entry = create_transaction_logNew(request, Bank_data,Party,'Bank not available',189,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Bank_data,0,'PartyBankDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})

class PartyBanksListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request,id=0):
        Bank_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = Bank_data['PartyID']
                Company = Bank_data['CompanyID']
                query = MC_PartyBanks.objects.filter(Party=Party, Company=Company)
                if query:
                    bank_serializer = PartyBanksSerializer(query, many=True).data
                    log_entry = create_transaction_logNew(request, Bank_data,Party,'Company:'+str(Company),190,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :bank_serializer})
                log_entry = create_transaction_logNew(request, Bank_data,Party,'Bank not available',190,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Bank_data,0,'PartyBankList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})


class PartyBanksSaveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        PartyBanks_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyBanks_serializer = PartyBanksSerializerSecond(data=PartyBanks_data, many=True)
                if PartyBanks_serializer.is_valid():
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': PartyBanks_serializer.data})
                    id = PartyBanks_serializer.data[0]['Party']
                    MC_PartyBanks_data = MC_PartyBanks.objects.filter(Party=id)
                    MC_PartyBanks_data.delete()
                    PartyBank = PartyBanks_serializer.save()
                    LastInsertID = PartyBank[0].id
                    log_entry = create_transaction_logNew(request, PartyBanks_data,id,'TransactionID:'+str(LastInsertID),191,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Banks Save Successfully','TransactionID':LastInsertID, 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, PartyBanks_data,id,'PartyBanksSave:'+str(PartyBanks_serializer.errors),34,0)
                    transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyBanks_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartyBanks_data,0,'PartyBanksSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data': []})


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
                    log_entry = create_transaction_logNew(request, bank_serializer,0,'',192,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :bank_serializer})
                log_entry = create_transaction_logNew(request, bank_serializer,0,'Bank not available',192,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'BankList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data':[]})

class BankView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        Bank_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Bank_serializer = BankSerializer(data=Bank_data)
                if Bank_serializer.is_valid():
                    Bank = Bank_serializer.save()
                    LastInsertID = Bank.id
                    log_entry = create_transaction_logNew(request, Bank_data,0,'TransactionID:'+str(LastInsertID),193,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Save Successfully','TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Bank_data,0,'BankSave:'+str(Bank_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Bank_serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Bank_data,0,'BankSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
    
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Bankdata = M_Bank.objects.get(id=id)
                Bank_serializer = BankSerializer(Bankdata)
                log_entry = create_transaction_logNew(request, Bank_serializer,0,f'Bank:{id}',367,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Bank_serializer.data})
        except  M_Bank.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Bank not available',367,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Bank Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,f'Bank:{id}'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
    @transaction.atomic()
    def put(self, request, id=0):
        Bankdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                BankdataByID = M_Bank.objects.get(id=id)
                Bank_serializer = BankSerializer(
                    BankdataByID, data=Bankdata)
                if Bank_serializer.is_valid():
                    Bank_serializer.save()
                    log_entry = create_transaction_logNew(request, Bankdata,0,'BankID:'+str(id),194,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, Bankdata,0,'BankEdit:'+str(Bank_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Bank_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Bankdata,0,'BankEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
    

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Bankdata = M_Bank.objects.get(id=id)
                Bankdata.delete()
                log_entry = create_transaction_logNew(request, 0,0,'BankID:'+str(id),195,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Deleted Successfully','Data':[]})
        except M_Bank.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'',195,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bank Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'BankDelete:'+'Bank used in transaction',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bank used in transaction', 'Data': []})
            
            




                








        