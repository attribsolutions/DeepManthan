from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_CreditDebit import *
from django.db.models import Sum
from ..models import *



class PurchaseReturnView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)
                Party = PurchaseReturndata['Party']
                Date = PurchaseReturndata['Date']
                a = GetMaxNumber.GetLoadingSheetNumber(Party,Date)
                PurchaseReturndata['No'] = str(a)
                PurchaseReturn_Serializer = PurchaseReturndata(data=PurchaseReturndata)
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    


