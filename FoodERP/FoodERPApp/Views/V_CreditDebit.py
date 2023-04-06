from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_CreditDebit import *
from django.db.models import Sum
from ..models import *


class CreditNotesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

     
    @transaction.atomic()
    def post(self,request):
        try:
            with transaction.atomic():
                Credit_Notedata = JSONParser().parse(request)
                Party = Credit_Notedata['Party']
                CreditNoteDate = Credit_Notedata['CreditNoteDate']
                query =  T_CreditNotes.objects.filter(Party=Party,CreditNoteDate=CreditNoteDate)
                if query:
                    CreditNote_Serializer = CreditNoteSerializer(query,many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :CreditNote_Serializer})
                else :
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'CreditNote Not Available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
        
class CreditNotesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication


    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                CreditNotedata = T_CreditNotes.objects.get(id=id)
                CreditNote_Serializer = CreditNoteSerializer(CreditNotedata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': CreditNote_Serializer.data})
        except  M_Bank.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'CreditNote Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Credit_Notedata = JSONParser().parse(request)
                CreditNotedataByID = T_CreditNotes.objects.get(id=id)
                CreditNote_Serializer = CreditNoteSerializer(CreditNotedataByID, data=Credit_Notedata)
                if CreditNote_Serializer.is_valid():
                    CreditNote_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CreditNote Updated Successfully','Data' :[]})
                else:
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CreditNote_Serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        