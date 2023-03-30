from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Receipts import *
from ..models import *


class ReceiptModeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                ReceiptJsondata = JSONParser().parse(request)
                CompanyID = ReceiptJsondata['Company']
                ReceiptmodeQuery = M_GeneralMaster.objects.filter(Company__in=[1,CompanyID]).filter(TypeID=3)
                
                if ReceiptmodeQuery.exists():
                    Receiptdata = ReceiptModeSerializer(ReceiptmodeQuery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Receiptdata})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Receipt Mode Not available ', 'Data': []})
        except M_GeneralMaster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Receipt Mode Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
        
        