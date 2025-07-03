from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *
from ..models import *
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction
from rest_framework.authentication import BasicAuthentication
from ..Serializer.S_Scheme import *
from rest_framework.views import APIView

     
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
                    SchemeDetails = M_Scheme.objects.raw(f'''SELECT M_Scheme.id, SchemeName, SchemeValue, ValueIn, FromPeriod, ToPeriod, 
                                                         FreeItemID, VoucherLimit, SchemeValueUpto,QrPrefix, SchemeTypeName, 
                                                         SchemeTypeID_id, UsageTime, BillAbove, UsageType, BillEffect, Column1, Column2, 
                                                         Column3,IsQrApplicable, M_Scheme.IsActive, concat(SchemeDetails,'',
                                                         ifnull(M_Parties.SAPPartyCode,'')) SchemeDetails, OverLappingScheme, Message, SchemeQuantity
                                                         FROM M_Scheme 
                                                         JOIN M_SchemeType ON M_Scheme.SchemeTypeID_id = M_SchemeType.id 
                                                         JOIN MC_SchemeParties ON MC_SchemeParties.SchemeID_id = M_Scheme.id
                                                         JOIN M_Parties ON M_Parties.id = MC_SchemeParties.PartyID_id  
                                                         WHERE PartyID_id = {Party} AND M_Scheme.IsActive = 1''')

                    data = []
                    for Scheme in SchemeDetails:
                        qr_codes = MC_SchemeQRs.objects.filter(SchemeID_id=Scheme.id).values('id', 'QRCode')
                        qr_list = [{"QRID": qr['id'], "QRCode": qr['QRCode']} for qr in qr_codes]

                        SchemeItems = MC_SchemeItems.objects.filter(SchemeID=Scheme.id).values(
                            'TypeForItem', 'Item', 'Quantity', 'DiscountValue', 'DiscountType'
                        )

                        mc_applicable_items = []
                        mc_not_applicable_items = []
                        mc_effective_items = []

                        applicable_ids = []
                        not_applicable_ids = []
                        effective_ids = []

                        for Item in SchemeItems:
                            item_data = {
                                "ItemID": Item['Item'],
                                "Quantity": Item['Quantity'],
                                "DiscountValue": Item['DiscountValue'],
                                "DiscountType": Item['DiscountType']
                            }

                            if Item['TypeForItem'] == 1:
                                mc_applicable_items.append(item_data)
                                applicable_ids.append(str(Item['Item']))
                            elif Item['TypeForItem'] == 2:
                                mc_not_applicable_items.append(item_data)
                                not_applicable_ids.append(str(Item['Item']))
                            elif Item['TypeForItem'] == 3:
                                mc_effective_items.append(item_data)
                                effective_ids.append(str(Item['Item']))

                        scheme_data = {
                            "SchemeId": Scheme.id,
                            "SchemeName": Scheme.SchemeName,
                            "SchemeTypeID": Scheme.SchemeTypeID_id,
                            "SchemeTypeName": Scheme.SchemeTypeName,
                            "SchemeDetails": Scheme.SchemeDetails,
                            "SchemeValue": Scheme.SchemeValue,
                            "SchemeQuantity" : Scheme.SchemeQuantity,
                            "ValueIn": Scheme.ValueIn,
                            "BillAbove": Scheme.BillAbove,
                            "VoucherLimit": Scheme.VoucherLimit,
                            "FromPeriod": Scheme.FromPeriod,
                            "ToPeriod": Scheme.ToPeriod,
                            "UsageType": Scheme.UsageType,
                            "UsageTime": Scheme.UsageTime,
                            "BillEffect": Scheme.BillEffect, 
                            "IsQrApplicable": Scheme.IsQrApplicable,
                            "QrPrefix": Scheme.QrPrefix,
                            "IsActive": Scheme.IsActive,
                            "FreeItemID": Scheme.FreeItemID,
                            "SchemeValueUpto": Scheme.SchemeValueUpto,
                            "OverLappingScheme" : Scheme.OverLappingScheme,
                            "Message" : Scheme.Message,
                            "Col1": Scheme.Column1,
                            "Col2": Scheme.Column2,
                            "Col3": Scheme.Column3,
                            "QR_Codes": qr_list,
                            "ItemsApplicable": ",".join(applicable_ids),
                            "ItemsNotApplicable": ",".join(not_applicable_ids),
                            "EffectiveItems": ",".join(effective_ids),
                            "ApplicableItemsDetails": mc_applicable_items,
                            "NotApplicableItemsDetails": mc_not_applicable_items,
                            "EffectiveItemsDetails": mc_effective_items,
                        }
                        data.append(scheme_data)

                if data:
                    create_transaction_logNew(request, data, 0, Party, 433, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': data})
                else:
                    create_transaction_logNew(request, data, Party, 'Record Not Found', 433, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            create_transaction_logNew(request, PartyData, 0, 'SchemeDetails:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})       
 
class SchemeListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                Scheme_data = M_Scheme.objects.all()
                Scheme_data_serializer = SchemeSerializer(Scheme_data,many=True)
                log_entry = create_transaction_logNew(request, Scheme_data_serializer,0,'',481,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Scheme_data_serializer.data})
        except  M_Scheme.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Scheme Data Does Not Exist',481,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Scheme Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllSchemes:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
class SchemeListperMonthView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request ):
        try:
            with transaction.atomic():
                SchemeData = JSONParser().parse(request)
                FromDate = SchemeData['FromDate']
                ToDate = SchemeData['ToDate']
                Scheme_data = M_Scheme.objects.raw(f'''SELECT id, SchemeName, FromPeriod, ToPeriod
                                                        FROM M_Scheme
                                                        WHERE FromPeriod <= '{ToDate}'  
                                                        AND ToPeriod >= '{FromDate}' ''')
                # print(Scheme_data)
                Scheme_data = SchemeSerializer1(Scheme_data,many=True)
                log_entry = create_transaction_logNew(request, Scheme_data,0,'',482,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Scheme_data.data})
        except  M_Scheme.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Scheme Data Does Not Exist',482,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Scheme Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllSchemes:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})

class SchemeTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                SchemeTypedata = JSONParser().parse(request)
                SchemeTypedata_Serializer = SchemeTypeSerializer(data=SchemeTypedata)
                if SchemeTypedata_Serializer.is_valid():
                    SchemeType = SchemeTypedata_Serializer.save()
                    LastInsertID = SchemeType.id
                    log_entry = create_transaction_logNew(request,SchemeTypedata,0,'TransactionID:'+str(LastInsertID),469,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Scheme Type Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,SchemeTypedata,0,'SchemeTypeSave:'+str(SchemeTypedata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  SchemeTypedata_Serializer.errors, 'Data':[]})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0,0,'SchemeTypeSave:'+str(Exception(e)),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
            
            
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                SchemeTypedata = JSONParser().parse(request)
                SchemeTypedataByID = M_SchemeType.objects.get(id=id)
                SchemeTypedata_Serializer = SchemeTypeSerializer(
                    SchemeTypedataByID, data=SchemeTypedata)
                if SchemeTypedata_Serializer.is_valid():
                    SchemeTypedata_Serializer.save()
                    log_entry = create_transaction_logNew(request,SchemeTypedata,0,0,470,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Scheme Type Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,SchemeTypedata,0,'SchemeTypeEdit:'+str(SchemeTypedata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SchemeTypedata_Serializer.errors, 'Data':[]})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0,0,Exception(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
            
           
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                SchemeType_data = M_SchemeType.objects.all()
                SchemeType_data_serializer = SchemeTypeSerializer(SchemeType_data,many=True)
                log_entry = create_transaction_logNew(request, SchemeType_data_serializer,0,'',471,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': SchemeType_data_serializer.data})
        except  M_SchemeType.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Scheme Type Data Does Not Exist',471,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Scheme Type Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllSchemeType:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
 

        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                SchemeTypedata = M_SchemeType.objects.get(id=id)
                SchemeTypedata.delete()
                log_entry = create_transaction_logNew(request,{'SchemeTypeID':id},0,'SchemeTypeID:'+str(id),472,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Scheme Type Deleted Successfully', 'Data':[]})
        except M_SchemeType.DoesNotExist:
            log_entry = create_transaction_logNew(request,{'SchemeTypeID':id},0,'SchemeTypeDelete:'+'Scheme Type Not available',472,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Scheme Type Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request,0,0,'SchemeTypeDelete:'+'Scheme Type used in another table',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Scheme Type used in another table', 'Data': []}) 
 
class SchemeTypsinglegetView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)       
    @transaction.atomic()
    def get(self, request,id=0 ):
        try:
            with transaction.atomic():
                SchemeType_data = M_SchemeType.objects.get(id=id)
                SchemeType_data_serializer = SchemeTypeSerializer(SchemeType_data)
                log_entry = create_transaction_logNew(request, SchemeType_data_serializer,0,'',475,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': SchemeType_data_serializer.data})
        except  M_SchemeType.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Scheme Type Data Does Not Exist',475,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Scheme Type Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllSchemeType:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
class SchemeDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)    
    serializer_class       = SchemeDetailsSerializer 
    @transaction.atomic()
    def get(self, request,SchemeID):       
        try:
            with transaction.atomic():
               
                    SchemeDetails = M_Scheme.objects.raw(f'''
                    SELECT 
                        M_Scheme.id, SchemeName, SchemeValue, ValueIn, FromPeriod, ToPeriod, FreeItemID, VoucherLimit, SchemeValueUpto, SchemeQuantity,
                        QrPrefix, SchemeTypeName, SchemeTypeID_id, UsageTime, BillAbove, UsageType, BillEffect, Column1, Column2, Column3,
                        IsQrApplicable, M_Scheme.IsActive, 
                        CONCAT(SchemeDetails, '', IFNULL(M_Parties.SAPPartyCode, '')) AS SchemeDetails, OverLappingScheme, Message,
                        M_Parties.id AS party_id, M_Parties.Name AS party_name,
                        M_Items.id AS item_id, M_Items.Name AS item_name,DiscountType,DiscountValue,Quantity,TypeForItem
                    FROM M_Scheme 
                    JOIN M_SchemeType ON M_Scheme.SchemeTypeID_id = M_SchemeType.id 
                    JOIN MC_SchemeParties ON MC_SchemeParties.SchemeID_id = M_Scheme.id
                    JOIN M_Parties ON M_Parties.id = MC_SchemeParties.PartyID_id  
                    LEFT JOIN MC_SchemeItems ON MC_SchemeItems.SchemeID_id = M_Scheme.id
                    LEFT JOIN M_Items ON M_Items.id = MC_SchemeItems.Item	                                
                    WHERE M_Scheme.id = {SchemeID} AND M_Scheme.IsActive = 1
                ''')

                    data = []
                    scheme_cache = {}

                    for row in SchemeDetails:
                        sid = row.id

                        if sid not in scheme_cache:
                            scheme_cache[sid] = {
                                "SchemeId":       row.id,
                                "SchemeName":     row.SchemeName,
                                "SchemeValue":    row.SchemeValue,
                                "SchemeQuantity": row.SchemeQuantity,
                                "ValueIn":        row.ValueIn,
                                "FromPeriod":     row.FromPeriod,
                                "ToPeriod":       row.ToPeriod,
                                "FreeItemID":     row.FreeItemID,
                                "VoucherLimit":   row.VoucherLimit,
                                "SchemeValueUpto": getattr(row, 'SchemeValueUpto', None),
                                "SchemeDetails" : row.SchemeDetails,
                                "OverLappingScheme" : row.OverLappingScheme,
                                "BillAbove":      row.BillAbove,
                                "QrPrefix":       row.QrPrefix,
                                "IsActive":       row.IsActive,
                                "SchemeTypeID":   row.SchemeTypeID_id,
                                "SchemeTypeName": row.SchemeTypeName,
                                "UsageTime":      row.UsageTime,
                                "UsageType":      row.UsageType,
                                "BillEffect":     row.BillEffect,
                                "ItemDetails":    {},
                                "PartyDetails":   {},
                            }

                        sc = scheme_cache[sid]

                        # Party Details
                        pid = getattr(row, 'party_id', None)
                        pname = getattr(row, 'party_name', '')
                        if pid and pid not in sc["PartyDetails"]:
                            sc["PartyDetails"][pid] = {
                                "PartyID": pid,
                                "PartyName": pname,
                            }

                        # Item Details
                        iid = getattr(row, 'item_id', None)
                        iname = getattr(row, 'item_name', '')
                        if iid and iid not in sc["ItemDetails"]:
                            sc["ItemDetails"][iid] = {
                                "ItemID": iid,
                                "ItemName": iname,
                                "DiscountType": row.DiscountType,
                                "DiscountValue": row.DiscountValue,
                                "Quantity": row.Quantity,
                                "TypeForItem": row.TypeForItem,

                            }

                    data = []
                    for sc in scheme_cache.values():
                        sc["PartyDetails"] = list(sc["PartyDetails"].values())
                        sc["ItemDetails"] = list(sc["ItemDetails"].values())
                        data.append(sc)
                    # print(data)
                    if data:
                        create_transaction_logNew(request, data, 0, SchemeID, 476, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': data})
                    else:
                        create_transaction_logNew(request, data, SchemeID, 'Record Not Found', 476, 0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            create_transaction_logNew(request, {}, 0, 'SchemeDetails: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
        

    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    Scheme = serializer.save()
                    LastInsertID = Scheme.id
                    log_entry = create_transaction_logNew(request,request.data,0,'TransactionID:'+str(LastInsertID),477,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Scheme Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,request.data,0,'SchemeSave:'+str(serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  serializer.errors, 'Data':[]})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0,0,'SchemeSave:'+str(Exception(e)),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})




    @transaction.atomic
    def put(self, request, id):
        try:
            data = JSONParser().parse(request)
            # print(data)
           
            # if user is None:
            #     log_entry = create_transaction_logNew(request, data, id, 'User not available', 478, 0)
            #     return JsonResponse({'StatusCode': 401, 'Status': False, 'Message': 'Unauthorized', 'Data': []})

            # scheme_id = data.get('SchemeID')

            # Update M_Scheme
            try:
                scheme = M_Scheme.objects.get(id=id)          
                scheme.SchemeName = data.get('SchemeName')                
                scheme.SchemeValue = data.get('SchemeValue')
                scheme.SchemeQuantity = data.get('SchemeQuantity')
                scheme.ValueIn = data.get('ValueIn')
                scheme.FromPeriod = data.get('FromPeriod')
                scheme.ToPeriod = data.get('ToPeriod')
                scheme.FreeItemID = data.get('FreeItemID')
                scheme.VoucherLimit = data.get('VoucherLimit')
                scheme.SchemeValueUpto = data.get('SchemeValueUpto')
                scheme.QrPrefix = data.get('QrPrefix')
                scheme.SchemeTypeID_id = data.get('SchemeTypeID')
                scheme.UsageTime = data.get('UsageTime')
                scheme.BillAbove = data.get('BillAbove')
                scheme.UsageType = data.get('UsageType')
                scheme.BillEffect = data.get('BillEffect')
                scheme.IsQrApplicable = data.get('IsQrApplicable')
                scheme.OverLappingScheme = data.get('OverLappingScheme')
                scheme.Message = data.get('Message')                
                
                scheme.save()
            except M_Scheme.DoesNotExist:
                log_entry = create_transaction_logNew(request, data, id, 'Scheme Not Found', 478, 0)
                return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'Scheme Not Found', 'Data': []})

            # Clear old Parties and Items
            MC_SchemeItems.objects.filter(SchemeID=id).delete()
            MC_SchemeParties.objects.filter(SchemeID=id).delete()

            # Insert updated Items
            for item in data.get('ItemDetails', []):
                MC_SchemeItems.objects.create(
                    SchemeID_id=id,
                    Item=item['Item'],                    
                    TypeForItem=item['TypeForItem'],
                    Quantity= item['Quantity'],
                    DiscountValue=item['DiscountValue'],
                    DiscountType=item['DiscountType']                   
                )

            # Insert updated Parties
            for party in data.get('PartyDetails', []):
                MC_SchemeParties.objects.create(
                    SchemeID_id=id,
                    PartyID_id=party['PartyID']
                )

            log_entry = create_transaction_logNew(request, data, id, 'Scheme updated', 478, 0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Scheme updated successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0, 'Scheme Update Error: ' + str(e), 478, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
        
        
    def delete(self,request,id=0):
        try:
            with transaction.atomic():
                scheme = M_Scheme.objects.get(id=id)
               
                # Delete related Scheme Items and Parties
                MC_SchemeItems.objects.filter(SchemeID=id).delete()
                MC_SchemeParties.objects.filter(SchemeID=id).delete()

                # Delete the Scheme itself
                scheme.delete()
                log_entry = create_transaction_logNew(request, {}, 0, id ,'Scheme deleted successfully', 479, 0)
                return Response({"message": "Scheme deleted successfully."}, status=status.HTTP_200_OK)

        except M_Scheme.DoesNotExist:
            log_entry = create_transaction_logNew(request, {}, 0, id,'Scheme not found', 479, 0)
            return Response({"error": "Scheme not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_entry = create_transaction_logNew(request, {}, 0, id, 479, 0)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


