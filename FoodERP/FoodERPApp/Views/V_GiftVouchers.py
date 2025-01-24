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
from ..Views.V_CommFunction import *
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
                VoucherExists = M_GiftVoucherCode.objects.filter(VoucherCode=coupon_code).exists()

                if not VoucherExists:
                    log_entry = create_transaction_logNew(request, 0,0,'',436,0)
                    return JsonResponse({'StatusCode': 404,'Status': False,
                        'Message': f"Invalid VoucherCode '{coupon_code}'. Do you want to continue saving the bill without using the voucher?",'Data': []})
            
                VoucherDetails = M_GiftVoucherCode.objects.filter(VoucherCode=coupon_code, IsActive=0).first()

                if VoucherDetails:
                    PartyName = "N/A"
                    if VoucherDetails.Party:
                        party = M_Parties.objects.filter(id=VoucherDetails.Party).first()
                        PartyName = party.Name if party else "N/A"

                    Invoice_Date = VoucherDetails.InvoiceDate.strftime('%Y-%m-%d') if VoucherDetails.InvoiceDate else "N/A"
                    Invoice_Number = VoucherDetails.InvoiceNumber if VoucherDetails.InvoiceNumber else "N/A"

                    message = (
                        f"The voucher code '{coupon_code}' is invalid as it has already been used with the following details:" + "\n"
                        f"- PartyName: {PartyName}" + "\n"
                        f"- InvoiceDate: {Invoice_Date}" + "\n"
                        f"- InvoiceNumber: {Invoice_Number}" + "\n"
                        "Would you like to proceed without applying the voucher?"
                    )
                    log_entry = create_transaction_logNew(request, 0,0,'',436,0)
                    return JsonResponse({'StatusCode': 204, 'Status': False, 'Message': message, 'Data': []})
                
                giftvoucherData = M_GiftVoucherCode.objects.filter(VoucherCode=coupon_code,IsActive=1)
                if giftvoucherData :
                        log_entry = create_transaction_logNew(request, 0,0,'',436,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Giftvoucher Code is Valid', 'Data': []})
                   
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETVoucherData:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

     
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
                    Party = giftvoucherData.get('Party', None)
                    client = giftvoucherData.get('client', 0)
                    
                    VoucherExists = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode).exists()

                    if not VoucherExists:
                        log_entry = create_transaction_logNew(request, giftvoucherData,Party,'',435,0)
                        return JsonResponse({'StatusCode': 404,'Status': False,
                            'Message': f"Invalid VoucherCode '{VoucherCode}'. Do you want to continue saving the bill without using the voucher?",'Data': []})
                
                    VoucherDetails = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode, IsActive=0).first()

                    if VoucherDetails:
                        PartyName = "N/A"
                        if VoucherDetails.Party:
                            party = M_Parties.objects.filter(id=VoucherDetails.Party).first()
                            PartyName = party.Name if party else "N/A"

                        Invoice_Date = VoucherDetails.InvoiceDate.strftime('%Y-%m-%d') if VoucherDetails.InvoiceDate else "N/A"
                        Invoice_Number = VoucherDetails.InvoiceNumber if VoucherDetails.InvoiceNumber else "N/A"

                        message = (
                            f"The voucher code '{VoucherCode}' is invalid as it has already been used with the following details:" + "\n"
                            f"- PartyName: {PartyName}" + "\n"
                            f"- InvoiceDate: {Invoice_Date}" + "\n"
                            f"- InvoiceNumber: {Invoice_Number}" + "\n"
                            "Would you like to proceed without applying the voucher?"
                        )
                        log_entry = create_transaction_logNew(request, giftvoucherData,Party,'',435,0)
                        return JsonResponse({'StatusCode': 204, 'Status': False, 'Message': message, 'Data': []})
                    
                    giftvoucherData = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode,IsActive=1).update(IsActive=0,InvoiceDate=InvoiceDate,
                                                                       InvoiceNumber=InvoiceNumber, InvoiceAmount=InvoiceAmount, Party=Party, client=client )
                    if giftvoucherData :
                        log_entry = create_transaction_logNew(request, giftvoucherData,Party,'',435,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Successfully Marked Gift Voucher Code is Used', 'Data': []})
                          
        except Exception as e:
            log_entry = create_transaction_logNew(request, giftvoucherData, 0,'GETVoucherData:'+str(e),33,0)
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

    
    
