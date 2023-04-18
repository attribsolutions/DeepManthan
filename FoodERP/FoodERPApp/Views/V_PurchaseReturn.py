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
                a = GetMaxNumber.GetPurchaseReturnNumber(Party,Date)
                PurchaseReturndata['ReturnNo'] = str(a)
                b = GetPrifix.GetPurchaseReturnPrifix(Party)
                PurchaseReturndata['FullReturnNumber'] = b+""+str(a)
                PurchaseReturn_Serializer = PurchaseReturnSerializer(data=PurchaseReturndata)
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Purchase Return Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PurchaseReturndata = T_PurchaseReturn.objects.get(id=id)
                PurchaseReturndata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data':[]})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Return used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
