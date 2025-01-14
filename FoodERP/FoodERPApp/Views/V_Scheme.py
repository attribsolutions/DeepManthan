from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *
from ..models import *


class SchemeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]    
    @transaction.atomic()
    def post(self, request):
        PartyData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                user=BasicAuthenticationfunction(request)
                
                Party = PartyData['Party']
                if user is not None:
                    SchemeDetails = M_Scheme.objects.raw(f'''select M_Scheme.id,SchemeName,SchemeValue,ValueIn,FromPeriod,ToPeriod,FreeItemID,VoucherLimit,QrPrefix,SchemeTypeName,SchemeTypeID_id,UsageTime,
                    BillAbove,UsageType,BillEffect,IsQrApplicable from M_Scheme 
                    JOIN M_SchemeType ON M_Scheme.SchemeTypeID_id=M_SchemeType.id 
                    JOIN MC_SchemeParties ON MC_SchemeParties.SchemeID_id=M_Scheme.id
                    Where PartyID={Party} and IsActive=1''');
                    data = []
                    for Scheme in SchemeDetails:   
                        
                        qr_codes = M_SchemeQRs.objects.filter(SchemeID_id=Scheme.id).values('id', 'QRCode')
                        qr_list = []
                        for qr in qr_codes:           
                            qr_list.append({"QRID": qr['id'], "QRCode": qr['QRCode']})
                        scheme_data={
                                "SchemeId": Scheme.id,
                                "SchemeName":Scheme.SchemeName,
                                "SchemeValue":Scheme.SchemeValue,
                                "ValueIn":Scheme.ValueIn,
                                "FromPeriod":Scheme.FromPeriod,
                                "ToPeriod":Scheme.ToPeriod,
                                "FreeItemID":Scheme.FreeItemID,
                                "VoucherLimit":Scheme.VoucherLimit,
                                "BillAbove":Scheme.BillAbove,
                                "QrPrefix":Scheme.QrPrefix,
                                "SchemeTypeID_id":Scheme.SchemeTypeID_id,
                                "SchemeTypeName":Scheme.SchemeTypeName,
                                "UsageTime":Scheme.UsageTime,
                                "UsageType":Scheme.UsageType,
                                "BillEffect":Scheme.BillEffect,                                     
                                "IsQrApplicable":Scheme.IsQrApplicable,
                                'QR_Codes': qr_list    
                            }
                            
                        data.append(scheme_data)
                        
                if data:                    
                    log_entry = create_transaction_logNew(request, PartyData, 0, 'SchemeDetails:' + str(data), 433, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': data})
                else:
                    log_entry = create_transaction_logNew(request, PartyData, Party, 'Record Not Found', 433, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
                    log_entry = create_transaction_logNew(request, PartyData, 0, 'SchemeDetails:' + str(e), 33, 0)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})       
    
                
    
               
     