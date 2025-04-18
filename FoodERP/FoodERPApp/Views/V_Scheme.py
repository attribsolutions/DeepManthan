from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *
from ..models import *
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction
from rest_framework.authentication import BasicAuthentication
from ..Serializer.S_Scheme import *


     
class SchemeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request):
        PartyData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                user = BasicAuthenticationfunction(request)
                Party = PartyData['Party']
                
                if user is not None:
                    SchemeDetails = M_Scheme.objects.raw(f'''
                        SELECT M_Scheme.id, SchemeName, SchemeValue, ValueIn, FromPeriod, ToPeriod, FreeItemID, VoucherLimit, SchemeValueUpto,
                        QrPrefix, SchemeTypeName, SchemeTypeID_id, UsageTime, BillAbove, UsageType, BillEffect, Column1, Column2, Column3,
                        IsQrApplicable, M_Scheme.IsActive, concat(SchemeDetails,'',ifnull(M_Parties.SAPPartyCode,'')) SchemeDetails, OverLappingScheme, Message
                        FROM M_Scheme 
                        JOIN M_SchemeType ON M_Scheme.SchemeTypeID_id = M_SchemeType.id 
                        JOIN MC_SchemeParties ON MC_SchemeParties.SchemeID_id = M_Scheme.id
                        join M_Parties on M_Parties.id=MC_SchemeParties.PartyID_id  
                                                         
                        WHERE PartyID_id = {Party} AND M_Scheme.IsActive = 1
                    ''')
                    
                    data = []
                    for Scheme in SchemeDetails:   
                        qr_codes = MC_SchemeQRs.objects.filter(SchemeID_id=Scheme.id).values('id', 'QRCode')
                        qr_list = [{"QRID": qr['id'], "QRCode": qr['QRCode']} for qr in qr_codes]

                        SchemeItems = MC_SchemeItems.objects.filter(SchemeID=Scheme.id).values('TypeForItem', 'Item')
                  
                        ItemsType = {1: [], 2: [], 3: []}
                        for Item in SchemeItems:
                            ItemsType[Item['TypeForItem']].append(str(Item['Item']))
                            
                        applicable_items = ",".join(ItemsType[1]) if ItemsType[1] else ""
                        non_applicable_items = ",".join(ItemsType[2]) if ItemsType[2] else ""
                        effective_items = ",".join(ItemsType[3]) if ItemsType[3] else ""

                        scheme_data = {
                            "SchemeId": Scheme.id,
                            "SchemeName": Scheme.SchemeName,
                            "SchemeValue": Scheme.SchemeValue,
                            "ValueIn": Scheme.ValueIn,
                            "FromPeriod": Scheme.FromPeriod,
                            "ToPeriod": Scheme.ToPeriod,
                            "FreeItemID": Scheme.FreeItemID,
                            "VoucherLimit": Scheme.VoucherLimit,
                            "BillAbove": Scheme.BillAbove,
                            "QrPrefix": Scheme.QrPrefix,
                            "IsActive": Scheme.IsActive,
                            "SchemeTypeID": Scheme.SchemeTypeID_id,
                            "SchemeTypeName": Scheme.SchemeTypeName,
                            "UsageTime": Scheme.UsageTime,
                            "UsageType": Scheme.UsageType,
                            "BillEffect": Scheme.BillEffect,                                     
                            "IsQrApplicable": Scheme.IsQrApplicable,
                            "SchemeDetails" : Scheme.SchemeDetails,
                            "OverLappingScheme" : Scheme.OverLappingScheme,
                            "SchemeValueUpto" : Scheme.SchemeValueUpto,
                            "Message" : Scheme.Message,
                            "Col1" : Scheme.Column1,
                            "Col2" : Scheme.Column2,
                            "Col3" : Scheme.Column3,
                            "QR_Codes": qr_list,
                            "ItemsApplicable": applicable_items,
                            "ItemsNotApplicable": non_applicable_items,
                            "EffectiveItems": effective_items
                        }
                        data.append(scheme_data)

                if data:
                    log_entry = create_transaction_logNew(request, data, 0, Party, 433, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': data})
                else:
                    log_entry = create_transaction_logNew(request, data, Party, 'Record Not Found', 433, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            log_entry =  create_transaction_logNew(request, PartyData, 0, 'SchemeDetails:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
        
 
class SchemeListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                Scheme_data = M_Scheme.objects.all()
                Scheme_data_serializer = SchemeSerializer(Scheme_data,many=True)
                log_entry = create_transaction_logNew(request, Scheme_data_serializer,0,'',328,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Scheme_data_serializer.data})
        except  M_Scheme.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Scheme Data Does Not Exist',328,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Scheme Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllSchemes:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
    
    


