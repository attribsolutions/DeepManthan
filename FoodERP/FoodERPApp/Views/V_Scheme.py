from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *
from ..models import *
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from django.contrib.auth import authenticate
import base64
from rest_framework import status
def BasicAuthenticationfunction(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
                    
        # Parsing the authorization header
        auth_type, auth_string = auth_header.split(' ', 1)
        if auth_type.lower() == 'basic':
            
            
            try:
                username, password = base64.b64decode(
                    auth_string).decode().split(':', 1)
            except (TypeError, ValueError, UnicodeDecodeError):
                return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                
        user = authenticate(request, username=username, password=password)
    return user
class SchemeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    # permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        PartyData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                user=BasicAuthenticationfunction(request)
                # print(user)
                Party = PartyData['Party']
                if user is not None:
                    SchemeDetails = M_Scheme.objects.raw(f'''select M_Scheme.id,SchemeName,SchemeValue,ValueIn,FromPeriod,ToPeriod,FreeItemID,VoucherLimit,QrPrefix,SchemeTypeName,SchemeTypeID_id,UsageTime,
                    BillAbove,UsageType,BillEffect,IsQrApplicable from M_Scheme 
                    JOIN M_SchemeType ON M_Scheme.SchemeTypeID_id=M_SchemeType.id 
                    JOIN MC_SchemeParties ON MC_SchemeParties.SchemeID_id=M_Scheme.id
                    Where PartyID=71064 and IsActive=1''');
                    
                    for Scheme in SchemeDetails:
                        print(Scheme)
                        scheme_dict = {}
                        if Scheme.id not in scheme_dict:
                            scheme_dict[Scheme.id] ={
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
                                'QR_Codes': []    
                            }
                        qr_codes = M_SchemeQRs.objects.filter(SchemeID_id=Scheme.id).values('id', 'QRCode')
                        for qr in qr_codes:
                            scheme_dict[Scheme.id]["QR_Codes"].append({
                                "QRID": qr['id'],
                                "QRCode": qr['QRCode']
                            })             
                
                    SchemeList = list(scheme_dict.values())
                    print(SchemeList)
                    if SchemeList:
                        log_entry = create_transaction_logNew(request, PartyData, 0, 'SchemeDetails:' + str(SchemeList), 390, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SchemeList})
                    else:
                        log_entry = create_transaction_logNew(request, PartyData, Party, 'Record Not Found', 390, 0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
                    log_entry = create_transaction_logNew(request, PartyData, 0, 'SchemeDetails:' + str(e), 33, 0)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})       
    
                
    
               
     