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
                ClientSaleID = giftvoucherData.get('ClientID',0)

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
                
                if VoucherCode == 'SSCCBM2025' :
                    
                    aa=M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode).values('InvoiceAmount')
                    
                    voucher_details.InvoiceAmount = float(aa[0]['InvoiceAmount'])+float(1)
                    voucher_details.save()
                else :
                    
                    voucher_details.IsActive = 0
                    voucher_details.InvoiceDate = InvoiceDate
                    voucher_details.InvoiceNumber = InvoiceNumber
                    voucher_details.InvoiceAmount = InvoiceAmount
                    voucher_details.Party = Party
                    voucher_details.client = client
                    voucher_details.ClientSaleID = ClientSaleID
                    voucher_details.save()

                log_entry = create_transaction_logNew(request, giftvoucherData, Party, '', 435, 0)
                return JsonResponse({'StatusCode': 200,'Status': True,'Message': 'Successfully Marked Gift Voucher Code as Used', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, giftvoucherData, 0, 'GETVoucherData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
    

class giftvouchervalidityCheck_Multiple(CreateAPIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]   
    
    @transaction.atomic()
    def patch(self, request):
        VoucherCodes = request.data.get("VoucherCode")
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication failed.")

        try:
            with transaction.atomic():            
                vouchers_qs = ( M_GiftVoucherCode.objects.filter(VoucherCode__in=VoucherCodes))
            voucher_map = {v.VoucherCode: v for v in vouchers_qs}

            valid_codes, invalid_codes, used_codes = [], [], []
            for code in VoucherCodes:
                    v = voucher_map.get(code)
                    if v is None:
                        invalid_codes.append({
                            "VoucherCode": code,
                            # "Message": (
                            #     f"Invalid VoucherCode '<b style=\"color:#FF5733;\">{code}</b>'.<br>"
                            #     "Do you want to continue saving the bill without using the voucher?"
                            # )
                        })
                        continue

                    if v.IsActive == 0:
                        party_name = "N/A"
                        if v.Party:
                            party_obj = M_Parties.objects.filter(id=v.Party).first()
                            party_name = party_obj.Name if party_obj else "N/A"

                        used_codes.append({
                            "VoucherCode": code,
                            "FranchiseName" : party_name,
                            "InvoiceDate" : v.InvoiceDate,
                            "InvoiceNumber" : v.InvoiceNumber
                            # "Message": (
                            #     f"The VoucherCode <b style=\"color:#4CAF50;\">'{code}'</b> has already been used.<br>"
                            #     "With the following details:<br>"
                            #     f"- <span style=\"color:#444\">FranchiseName:</span> "
                            #     f"<span style=\"color:#007BFF;\">{party_name}</span><br>"
                            #     f"- <span style=\"color:#444\">InvoiceDate:</span> "
                            #     f"<span style=\"color:#007BFF;\">{v.InvoiceDate:%Y-%m-%d}</span><br>"
                            #     f"- <span style=\"color:#444\">InvoiceNumber:</span> "
                            #     f"<span style=\"color:#007BFF;\">{v.InvoiceNumber or 'N/A'}</span><br>"
                            #     "<b></br>Would you like to proceed without applying the voucher?</b>"
                            # )
                        })
                        continue
                    
                    valid_codes.append({
                        "VoucherCode": code,
                        # "Message": (
                        #     f"The VoucherCode <b style=\"color:#4CAF50;\">'{code}'</b> is valid and can be used.<br>"
                        #     "Would you like to proceed with applying this voucher?"
                        # )
                    })                 

            status_code = 200 if valid_codes else 204 if used_codes else 404
           
            log_entry = create_transaction_logNew(request, 0, 0, '', 468 if status_code == 200 else 0, 0)
            return JsonResponse({"StatusCode": status_code,"Status": bool(valid_codes),"Message": "Gift voucher validation result.",
                                "Data": {"Valid": valid_codes,"Invalid": invalid_codes,"Used": used_codes}})            
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'GETVoucherData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})  
    
    @transaction.atomic()
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication failed.")

        giftvoucherDataList = JSONParser().parse(request)

        try:
            with transaction.atomic():
                updated_vouchers = []
                invalid_vouchers = []
                used_vouchers = []

                for data in giftvoucherDataList:
                    VoucherCode = data.get('VoucherCode')

                    # fetch voucher
                    voucher_details = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode).first()

                    if not voucher_details:
                        invalid_vouchers.append({
                            "VoucherCode": VoucherCode,
                            "Message": f"Invalid VoucherCode '{VoucherCode}'."
                        })
                        continue

                    if voucher_details.IsActive == 0:
                        PartyName = "N/A"
                        if voucher_details.Party:
                            party = M_Parties.objects.filter(id=voucher_details.Party).first()
                            PartyName = party.Name if party else "N/A"

                        Invoice_Date = voucher_details.InvoiceDate.strftime('%Y-%m-%d') if voucher_details.InvoiceDate else "N/A"
                        Invoice_Number = voucher_details.InvoiceNumber if voucher_details.InvoiceNumber else "N/A"

                        used_vouchers.append({
                            "VoucherCode": VoucherCode,
                            "FranchiseName": PartyName,
                            "InvoiceDate": Invoice_Date,
                            "InvoiceNumber": Invoice_Number,
                            "Message": f"The VoucherCode '{VoucherCode}' has already been used."
                        })
                        continue

                    # Special voucher code logic
                    if VoucherCode == 'SSCCBM2025':
                        aa = M_GiftVoucherCode.objects.filter(VoucherCode=VoucherCode).values('InvoiceAmount')
                        new_amount = float(aa[0]['InvoiceAmount']) + 1 if aa and aa[0]['InvoiceAmount'] else 1
                        voucher_details.InvoiceAmount = new_amount
                    else:
                        voucher_details.IsActive = 0
                        voucher_details.InvoiceDate = data.get('InvoiceDate')
                        voucher_details.InvoiceNumber = data.get('InvoiceNumber')
                        voucher_details.InvoiceAmount = data.get('InvoiceAmount')
                        voucher_details.Party = data.get('Party')
                        voucher_details.client = data.get('client', 0)
                        voucher_details.ClientSaleID = data.get('ClientID', 0)
                      
                    voucher_details.save()

                    updated_vouchers.append({
                        "VoucherCode": VoucherCode,
                        "Message": "Voucher updated successfully."})

                status_code = 200 if updated_vouchers else (204 if used_vouchers else 404)

                log_entry = create_transaction_logNew(request, giftvoucherDataList, 0, '', 470 if status_code == 200 else 0, 0)

                return JsonResponse({'StatusCode': status_code,'Status': bool(updated_vouchers),'Message': 'Gift voucher save process completed.',
                                    'Data': {'Updated': updated_vouchers,'Invalid': invalid_vouchers,'Used': used_vouchers}})

        except Exception as e:
            log_entry = create_transaction_logNew(request, giftvoucherDataList, 0, 'SaveMultiVoucherData:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400,'Status': False,'Message': str(e),'Data': []})

        
        

class GiftVoucherList(CreateAPIView):
    
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
           
    # @transaction.atomic()
    # def get(self, request ):
    #     try:
    #         with transaction.atomic():
                
    #             GiftVoucher_Data = M_GiftVoucherCode.objects.all()
    #             GiftVoucher_Data_serializer = GiftVoucherSerializer(GiftVoucher_Data,many=True)
    #             log_entry = create_transaction_logNew(request, GiftVoucher_Data_serializer,0,'',437,0)
    #             return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': GiftVoucher_Data_serializer.data})
    #     except  M_GiftVoucherCode.DoesNotExist:
    #         log_entry = create_transaction_logNew(request,0,0,'GiftVoucher Does Not Exist',437,0)
    #         return JsonResponse({'StatusCode': 204, 'Status': False,'Message':  'GiftVoucher Not available', 'Data': []})
    #     except Exception as e:
    #         log_entry = create_transaction_logNew(request, 0, 0,'GETAllGiftVoucher:'+str(e),33,0)
    #         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
     
    @transaction.atomic()
    def put(self, request, id=0):
        GiftVoucher_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GiftVoucherDataByID = M_GiftVoucherCode.objects.get(id=id)
                GiftVoucher_Data_serializer = GiftVoucherSerializer(GiftVoucherDataByID, data=GiftVoucherSerializer)
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

        
    @transaction.atomic()
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication failed.")

        data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = data.get('FromDate', None)
                ToDate = data.get('ToDate', None)
                PartyID = data.get('PartyID', None)
               
                valid_vouchers = M_GiftVoucherCode.objects.filter(Party=PartyID, IsActive=False,UpdatedOn__date__range=[FromDate, ToDate]
                                                                ).values( 'VoucherCode', 'InvoiceDate', 'InvoiceNumber', 'InvoiceAmount')
                if not valid_vouchers.exists():
                    log_entry = create_transaction_logNew(request,data,PartyID,'GiftVoucher Does Not Exist',437,0)
                    return JsonResponse({'StatusCode': 404,'Status': False,'Message': "No valid voucher codes found for the specified criteria.",'Data': []})
                vouchers_list = list(valid_vouchers)
                log_entry = create_transaction_logNew(request, data,PartyID,'',437,0)
                return JsonResponse({'StatusCode': 200,'Status': True,'Message': "Valid VoucherCodes retrieved successfully.",'Data': vouchers_list })

        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0, 'ValidVoucherData: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400,'Status': False,'Message': str(e),'Data': [] })


class GiftVoucherUploadView(CreateAPIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]


    @transaction.atomic()
    def post(self, request):
        data = JSONParser().parse(request)
        try:
            vouchers = data.get('Data', [])
            scheme_id = data.get('Scheme', None)

            if not scheme_id:
                log_entry = create_transaction_logNew(request,data,0,'Scheme ID is required',483,0)
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Scheme ID is required', 'Data': []})

            if not vouchers:
                log_entry = create_transaction_logNew(request,data,0,'No voucher data provided for SchemeID:'+str(scheme_id),483,0)
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'No voucher data provided', 'Data': []})

            if not M_Scheme.objects.filter(id=scheme_id).exists():
                log_entry = create_transaction_logNew(request,data,0,'Invalid SchemeID:'+str(scheme_id),483,0)
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid Scheme ID', 'Data': []})

            voucher_codes = [voucher.get('Voucher') for voucher in vouchers if voucher.get('Voucher')]

            existing_vouchers = M_GiftVoucherCode.objects.filter(VoucherCode__in=voucher_codes, Scheme_id=scheme_id).values_list('VoucherCode', flat=True)

            if existing_vouchers:
                log_entry = create_transaction_logNew(request, data, 0, f'Duplicate vouchers: {",".join(existing_vouchers)}', 483, 0)
                return JsonResponse({'StatusCode': 400,'Status': False,'Message': f'These voucher codes already exist for this scheme: {", ".join(existing_vouchers)}','Data': []})

            VoucherTypeID = 196
            voucher_objects = [M_GiftVoucherCode(VoucherCode=code,IsActive=True,Party=0,client=0,ClientSaleID=0,VoucherType_id=VoucherTypeID,Scheme_id=scheme_id)
                for code in voucher_codes
            ]

            if voucher_objects:
                M_GiftVoucherCode.objects.bulk_create(voucher_objects)
                log_entry = create_transaction_logNew(request, data, 0, 'Gift Vouchers saved for SchemeID:'+str(scheme_id), 483, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Gift Vouchers saved successfully', 'Data': []})
            else:
                log_entry = create_transaction_logNew(request, data, 0, 'No valid voucher data Found', 483, 0)
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'No valid voucher data found', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0, 'VoucherDetails: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

        
        
class DeleteGiftVouchersBySchemeView(CreateAPIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                if not M_Scheme.objects.filter(id=id).exists():
                    log_entry = create_transaction_logNew(request, 0, 0, 'Scheme ID not available', 484, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Scheme ID not available', 'Data': []})
                
                vouchers = M_GiftVoucherCode.objects.filter(Scheme_id=id)

                if not vouchers.exists():
                    log_entry = create_transaction_logNew(request, 0, 0, 'No vouchers found for SchemeID:'+str(id), 484, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'No vouchers found for this Scheme', 'Data': []})

                if vouchers.filter(IsActive=False).exists():
                    log_entry = create_transaction_logNew(request, 0, 0, 'Some vouchers are active for SchemeID:'+str(id), 484, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Voucher data used in another table', 'Data': []})
                
                DeleteCount, DeleteVouchers = vouchers.delete()

                log_entry = create_transaction_logNew(request, 0, 0, f'Deleted {DeleteCount} vouchers for SchemeID:{id}', 484, 0)
                return JsonResponse({'StatusCode': 200,'Status': True,'Message': f'{DeleteCount} vouchers deleted successfully','Data': []})

        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0, 0, 'GiftVoucherCode data used in another table', 8, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'GiftVoucherCode data used in another table', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'VoucherDeletion:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
