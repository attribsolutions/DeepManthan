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
                        
                        return JsonResponse({'StatusCode': 204, 'Status': False,'Message': 'Giftvoucher Code is InValid', 'Data': []})
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
                    InvoiceDate = giftvoucherData.get('InvoiceDate', None)
                    InvoiceNumber = giftvoucherData.get('InvoiceNumber', None)
                    InvoiceAmount = giftvoucherData.get('InvoiceAmount', None)
                    
                    giftvoucherData = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode,IsActive=1).update(IsActive=0,InvoiceDate=InvoiceDate,
                                                                       InvoiceNumber=InvoiceNumber, InvoiceAmount=InvoiceAmount)
                    if giftvoucherData :
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Successfully marked Gift voucher Code is used', 'Data': []})
                    else:
                        # log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                        return JsonResponse({'StatusCode': 204, 'Status': False,'Message': 'Giftvoucher Code is InValid', 'Data': []})       
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
        except  M_GiftVoucherCode.DoesNotExist:
            # log_entry = create_transaction_logNew(request,0,0,'GiftVoucher Does Not Exist',328,0)
            return JsonResponse({'StatusCode': 204, 'Status': False,'Message':  'GiftVoucher Not available', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'GETAllGiftVoucher:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
     
    @transaction.atomic()
    def put(self, request, id=0):
        GiftVoucher_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GiftVoucherDataByID = M_GiftVoucherCode.objects.get(id=id)
                GiftVoucher_Data_serializer = GiftVoucherSerializer(
                    GiftVoucherDataByID, data=GiftVoucherSerializer)
                if GiftVoucher_Data_serializer.is_valid():
                    GiftVoucher_Data_serializer.save()
                    # log_entry = create_transaction_logNew(request, GiftVoucher_Data,0,'GiftVoucherID:'+str(id),330,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GiftVoucher_Data Updated Successfully','Data' :[]})
                else:
                    # log_entry = create_transaction_logNew(request, GiftVoucher_Data,0,'GiftVoucherEdit:'+str(Cluster_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': False, 'Message': GiftVoucher_Data_serializer.errors, 'Data' :[]})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, GiftVoucher_Data, 0,'GiftVoucherEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GiftVoucher_Data = M_GiftVoucherCode.objects.get(id=id)
                GiftVoucher_Data.delete()
                # log_entry = create_transaction_logNew(request, 0,0,'GiftVoucherID:'+str(id),332,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GiftVoucher_Data Deleted Successfully','Data':[]})
        except M_GiftVoucherCode.DoesNotExist:
            # log_entry = create_transaction_logNew(request, 0,0,'GiftVoucher_Data Not available',332,0)
            return JsonResponse({'StatusCode': 204, 'Status': False, 'Message':'GiftVoucher_Data Not available', 'Data': []})
        except IntegrityError:  
            # log_entry = create_transaction_logNew(request, 0,0,'GiftVoucher_Data used in another table',8,0)    
            return JsonResponse({'StatusCode': 204, 'Status': False, 'Message':'GiftVoucher_Data used in another table', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0,0,'GiftVoucherDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})   

    
    
