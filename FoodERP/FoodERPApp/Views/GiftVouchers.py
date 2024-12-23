from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from SweetPOS.Views.SweetPOSCommonFunction import BasicAuthenticationfunction
from rest_framework.authentication import BasicAuthentication
from ..models import *

class giftvouchervalidityCheck(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    @transaction.atomic()
    def get(self, request, coupon_code):
        try:
            with transaction.atomic():
                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                    giftvoucherData = M_GiftVoucherCode.objects.filter(VoucherCode=coupon_code,IsActive=1)
                    giftvoucherDatacount = giftvoucherData.count()
                    if giftvoucherDatacount > 0:
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Giftvoucher Code is Valid', 'Data': []})
                    else:
                        
                        return JsonResponse({'StatusCode': 200, 'Status': False,'Message': 'Giftvoucher Code is InValid', 'Data': []})
                else:
                    # log_entry = create_transaction_logNew(request,0, DivisionID, "ItemList Not available",392,0)
                    return JsonResponse({'status': False, 'status_code': 401, 'message': 'Unauthorized'}) 
        
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETSingleCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
    @transaction.atomic()
    def post(self, request):
        giftvoucherData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                
                    VoucherCode = giftvoucherData['VoucherCode']
                    giftvoucherData = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode,IsActive=1).update(IsActive=0)
                    if giftvoucherData :
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Successfully marked Gift voucher Code is used', 'Data': []})
                    else:
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 200, 'Status': False,'Message': 'Giftvoucher Code is InValid', 'Data': []})
                else:
                    # log_entry = create_transaction_logNew(request,0, DivisionID, "ItemList Not available",392,0)
                    return JsonResponse({'status': False, 'status_code': 401, 'message': 'Unauthorized'}, status=401) 
        
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETSingleCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})    