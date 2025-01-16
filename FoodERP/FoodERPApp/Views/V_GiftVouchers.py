from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from SweetPOS.Views.SweetPOSCommonFunction import BasicAuthenticationfunction
from rest_framework.authentication import BasicAuthentication
from ..models import *
from ..Serializer.S_GiftVouchers import *


class giftvouchervalidityCheck(CreateAPIView):
    
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic()
    def get(self, request, coupon_code):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication failed.")
        try:
            with transaction.atomic():
                # user=BasicAuthenticationfunction(request)
                    
                # if user is not None:
                    giftvoucherData = M_GiftVoucherCode.objects.filter(VoucherCode=coupon_code,IsActive=1)
                    giftvoucherDatacount = giftvoucherData.count()
                    if giftvoucherDatacount > 0:
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Giftvoucher Code is Valid', 'Data': []})
                    else:
                        
                        return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Giftvoucher Code is InValid', 'Data': []})
                # else:
                #     # log_entry = create_transaction_logNew(request,0, DivisionID, "ItemList Not available",392,0)
                #     return JsonResponse({'status': False, 'status_code': 401, 'message': 'Unauthorized'}) 
        
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETSingleCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
    @transaction.atomic()
    def post(self, request):
        
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication failed.")
        
        giftvoucherData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                # user=BasicAuthenticationfunction(request)
                    
                # if user is not None:
                
                    VoucherCode = giftvoucherData['VoucherCode']
                    InvoiceDate = giftvoucherData.get('InvoiceDate')
                    InvoiceNumber = giftvoucherData.get('InvoiceNumber')
                    InvoiceAmount = giftvoucherData.get('InvoiceAmount')
                    Party = giftvoucherData.get('Party')
                    
                    giftvoucherData = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode,IsActive=1,Party=Party).update(IsActive=0,InvoiceDate=InvoiceDate,
                                                                       InvoiceNumber=InvoiceNumber, InvoiceAmount=InvoiceAmount)
                    if giftvoucherData :
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Successfully marked Gift voucher Code is used', 'Data': []})
                    else:
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Giftvoucher Code is InValid', 'Data': []})
                # else:
                #     # log_entry = create_transaction_logNew(request,0, DivisionID, "ItemList Not available",392,0)
                #     return JsonResponse({'status': False, 'status_code': 401, 'message': 'Unauthorized'}, status=401) 
        
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETSingleCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})    
        


class GiftVoucherList(CreateAPIView):
    
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
           
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                
                GiftVoucher_Data = M_GiftVoucherCode.objects.all()
                GiftVoucher_Data_serializer = GiftVoucherSerializer(GiftVoucher_Data,many=True)
                # log_entry = create_transaction_logNew(request, GiftVoucher_Data_serializer,0,'',328,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': GiftVoucher_Data_serializer.data})
        except  M_Cluster.DoesNotExist:
            # log_entry = create_transaction_logNew(request,0,0,'GiftVoucher Does Not Exist',328,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'GiftVoucher Not available', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETAllGiftVoucher:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
    
    
