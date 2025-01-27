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
                VoucherDetails = M_GiftVoucherCode.objects.filter(VoucherCode=coupon_code).first()

                if not VoucherDetails:
                    log_entry = create_transaction_logNew(request, 0, 0, '', 436, 0)
                    return JsonResponse({
                        'StatusCode': 404, 'Status': False,
                         'Message': f"Invalid VoucherCode '<b style=\"color: #FF5733;\">{coupon_code}</b>'.<br></br>"
                         f"Do you want to continue saving the bill without using the voucher?", 'Data': []})

                if VoucherDetails.IsActive == 0:
                    PartyName = "N/A"
                    if VoucherDetails.Party:
                        party = M_Parties.objects.filter(id=VoucherDetails.Party).first()
                        PartyName = party.Name if party else "N/A"

                    Invoice_Date = VoucherDetails.InvoiceDate.strftime('%Y-%m-%d') if VoucherDetails.InvoiceDate else "N/A"
                    Invoice_Number = VoucherDetails.InvoiceNumber if VoucherDetails.InvoiceNumber else "N/A"

                    message = (
                                f"The VoucherCode <b style=\"color: #4CAF50;\">'{coupon_code}'</b> has already been used.<br>"
                                f"With the following details:<br>"
                                f"- <span style=\"color: #444444;\">FranchiseName:</span> <span style=\"color: #007BFF;\">{PartyName}</span><br>"
                                f"- <span style=\"color: #444444;\">InvoiceDate:</span> <span style=\"color: #007BFF;\">{Invoice_Date}</span><br>"
                                f"- <span style=\"color: #444444;\">InvoiceNumber:</span> <span style=\"color: #007BFF;\">{Invoice_Number}</span><br>"
                                f"<b></br>Would you like to proceed without applying the voucher?</b>"
                            )

                    log_entry = create_transaction_logNew(request, 0, 0, '', 436, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': False, 'Message': message, 'Data': []})

                if VoucherDetails.IsActive == 1:
                    log_entry = create_transaction_logNew(request, 0, 0, '', 436, 0)
                    return JsonResponse({ 'StatusCode': 200,'Status': True,'Message': 'Giftvoucher Code is Valid','Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'GETVoucherData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})


    @transaction.atomic()
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication failed.")

        giftvoucherData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                VoucherCode = giftvoucherData['VoucherCode']
                InvoiceDate = giftvoucherData.get('InvoiceDate', None)
                InvoiceNumber = giftvoucherData.get('InvoiceNumber', None)
                InvoiceAmount = giftvoucherData.get('InvoiceAmount', None)
                Party = giftvoucherData.get('Party', None)
                client = giftvoucherData.get('client', 0)

                voucher_details = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode).first()

                if not voucher_details:
                    log_entry = create_transaction_logNew(request, giftvoucherData, Party, '', 435, 0)
                    return JsonResponse({'StatusCode': 404,'Status': False,
                                        'Message': f"Invalid VoucherCode '<b style=\"color: #FF5733;\">{VoucherCode}</b>'.<br></br>"
                                                    f"Do you want to continue saving the bill without using the voucher?", 'Data': []})
                if voucher_details.IsActive == 0:
                    PartyName = "N/A"
                    if voucher_details.Party:
                        party = M_Parties.objects.filter(id=voucher_details.Party).first()
                        PartyName = party.Name if party else "N/A"

                    Invoice_Date = voucher_details.InvoiceDate.strftime('%Y-%m-%d') if voucher_details.InvoiceDate else "N/A"
                    Invoice_Number = voucher_details.InvoiceNumber if voucher_details.InvoiceNumber else "N/A"

                    message = (
                                f"The VoucherCode <b style=\"color: #4CAF50;\">'{VoucherCode}'</b> has already been used.<br>"
                                f"With the following details:<br>"
                                f"- <span style=\"color: #444444;\">FranchiseName:</span> <span style=\"color: #007BFF;\">{PartyName}</span><br>"
                                f"- <span style=\"color: #444444;\">InvoiceDate:</span> <span style=\"color: #007BFF;\">{Invoice_Date}</span><br>"
                                f"- <span style=\"color: #444444;\">InvoiceNumber:</span> <span style=\"color: #007BFF;\">{Invoice_Number}</span><br>"
                                f"<b></br>Would you like to proceed without applying the voucher?</b>"
                            )
                    
                    log_entry = create_transaction_logNew(request, giftvoucherData, Party, '', 435, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': False, 'Message': message,'Data': []})
                voucher_details.IsActive = 0
                voucher_details.InvoiceDate = InvoiceDate
                voucher_details.InvoiceNumber = InvoiceNumber
                voucher_details.InvoiceAmount = InvoiceAmount
                voucher_details.Party = Party
                voucher_details.client = client
                voucher_details.save()

                log_entry = create_transaction_logNew(request, giftvoucherData, Party, '', 435, 0)
                return JsonResponse({'StatusCode': 200,'Status': True,'Message': 'Successfully Marked Gift Voucher Code as Used', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, giftvoucherData, 0, 'GETVoucherData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

class GiftVoucherList(CreateAPIView):
    
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
           
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                
                GiftVoucher_Data = M_GiftVoucherCode.objects.all()
                GiftVoucher_Data_serializer = GiftVoucherSerializer(GiftVoucher_Data,many=True)
                log_entry = create_transaction_logNew(request, GiftVoucher_Data_serializer,0,'',437,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': GiftVoucher_Data_serializer.data})
        except  M_GiftVoucherCode.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'GiftVoucher Does Not Exist',437,0)
            return JsonResponse({'StatusCode': 204, 'Status': False,'Message':  'GiftVoucher Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllGiftVoucher:'+str(e),33,0)
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
                    log_entry = create_transaction_logNew(request, GiftVoucher_Data,0,'GiftVoucherID:'+str(id),438,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GiftVoucher_Data Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, GiftVoucher_Data,0,'GiftVoucherEdit:'+str(GiftVoucher_Data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': False, 'Message': GiftVoucher_Data_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, GiftVoucher_Data, 0,'GiftVoucherEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GiftVoucher_Data = M_GiftVoucherCode.objects.get(id=id)
                GiftVoucher_Data.delete()
                log_entry = create_transaction_logNew(request, 0,0,'GiftVoucherID:'+str(id),439,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GiftVoucher_Data Deleted Successfully','Data':[]})
        except M_GiftVoucherCode.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'GiftVoucher_Data Not available',439,0)
            return JsonResponse({'StatusCode': 204, 'Status': False, 'Message':'GiftVoucher_Data Not available', 'Data': []})
        except IntegrityError:  
            log_entry = create_transaction_logNew(request, 0,0,'GiftVoucher_Data used in another table',8,0)    
            return JsonResponse({'StatusCode': 204, 'Status': False, 'Message':'GiftVoucher_Data used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GiftVoucherDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})   

    
    
