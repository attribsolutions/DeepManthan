import base64
import datetime
from datetime import datetime, timedelta
import json
from time import strftime
from django.contrib.auth import authenticate
from base64 import b64decode
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from ..Views.V_CommFunction import *
from ..Serializer.S_SAPApi import InvoiceSerializer,InvoiceToSCMSerializer
from ..Serializer.S_Orders import *
from ..models import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
import requests
import xml.etree.ElementTree as ET
import xmltodict
import json
from django.db.models import Sum, Q


class SAPInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                
                aa = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                # CustomPrint(auth_header)
                if auth_header:
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    user = authenticate(request, username=username, password=password)
                    InvoiceItems = list()
                    if user is not None:

                        if aa['refInvoiceNo']:
                            
                            CheckIsInwardornot=T_Invoices.objects.raw('''SELECT Invoice_id id,Inward FROM TC_GRNReferences join T_Invoices on Invoice_id=T_Invoices.id where T_Invoices.FullInvoiceNumber = %s ''',[aa["refInvoiceNo"]])
                            if CheckIsInwardornot:
                                hidedeletedInvoice=T_Invoices.objects.filter(FullInvoiceNumber=aa["refInvoiceNo"]).update(DeletedFromSAP=1)
                                log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+aa["InvoiceNumber"],285,0)
                                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice already Inwarded', 'Data': []})
                            else:
                                Delete_Invoice=T_Invoices.objects.filter(FullInvoiceNumber=aa["refInvoiceNo"]).delete()
                                log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+aa["InvoiceNumber"],286,0)
                                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Delete Successfully', 'Data': []})

                        else:
                            
                        
                            DuplicateCheck = T_Invoices.objects.filter(
                                FullInvoiceNumber=aa["InvoiceNumber"])
                            # CustomPrint('aaaaaaa')
                            if(DuplicateCheck.count() == 0):
                                    
                                # CustomPrint('bbbbbb')   
                                CustomerMapping = M_Parties.objects.filter(
                                    SAPPartyCode=aa['CustomerID']).values("id", "GSTIN")
                                PartyMapping = M_Parties.objects.filter(
                                    SAPPartyCode=aa['Plant']).values("id")
                                # CustomPrint('ccccccccc')
                                if CustomerMapping.exists():
                                    aa['Customer'] = CustomerMapping
                                else:
                                    log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+aa["InvoiceNumber"],287,0)
                                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Customer Data ", 'Data': []})
                                # CustomPrint('dddddddddd')
                                if PartyMapping.exists():
                                    aa['Party'] = PartyMapping
                                else:
                                    log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+aa["InvoiceNumber"],288,0)
                                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Plant Data ", 'Data': []})

                                InvoiceDate = datetime.strptime(
                                    aa['InvoiceDate'], "%d.%m.%Y").strftime("%Y-%m-%d")
                                
                                for bb in aa['InvoiceItems']:

                                    if str(bb['BatchCode']) == '':
                                        log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+aa["InvoiceNumber"],318,0)
                                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': "Blank BatchCode Is Not Allowed", 'Data': []})

                                    if str(bb['BatchDate']) == '':
                                        log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+aa["InvoiceNumber"],319,0)
                                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': "Blank BatchDate Is Not Allowed", 'Data': []})
                                    else:
                                        if str(bb['BatchDate']) == "00.00.0000":
                                            current_date = date.today()
                                            # Format the date as yyyy-mm-dd             
                                            BatchDate = current_date.strftime('%Y-%m-%d')
                                        else:
                                            BatchDate = datetime.strptime(bb['BatchDate'], "%d.%m.%Y").strftime("%Y-%m-%d")

                                    
                                    
                                    ItemMapping = M_Items.objects.filter(
                                        SAPItemCode=bb['MaterialCode']).values("id")
                                    UnitMapping = M_Units.objects.filter(
                                        SAPUnit=bb['BaseUOM']).values("id")
                                    
                                
                                    if ItemMapping.exists():
                                        bb['Item'] = ItemMapping
                                    else:
                                        log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+aa["InvoiceNumber"],289,0)
                                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Material Code", 'Data': []})

                                    if UnitMapping.exists():
                                        # CustomPrint('gggggggggg')
                                        MC_UnitID = MC_ItemUnits.objects.filter(
                                            UnitID=UnitMapping[0]["id"], Item=ItemMapping[0]["id"], IsDeleted=0).values("id")
                                        # CustomPrint(MC_UnitID)

                                        if MC_UnitID.exists():
                                            bb['Unit'] = MC_UnitID
                                        else:
                                            log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+ aa["InvoiceNumber"],290,0)
                                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Item Unit ", 'Data': []})
                                    else:
                                        log_entry = create_transaction_logNew(request, aa, 0, aa["InvoiceNumber"],291,0)
                                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Unit Code", 'Data': []})
                                    # CustomPrint('hhhhhhhhhhhh')
                                    BaseUnitQuantity = UnitwiseQuantityConversion(
                                        ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 0, 0).GetBaseUnitQuantity()
                                    QtyInNo = UnitwiseQuantityConversion(
                                        ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 1, 0).ConvertintoSelectedUnit()
                                    QtyInKg = UnitwiseQuantityConversion(
                                        ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 2, 0).ConvertintoSelectedUnit()
                                    QtyInBox = UnitwiseQuantityConversion(
                                        ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 4, 0).ConvertintoSelectedUnit()
                                    # CustomPrint('iiiiiiiiiii')
                                    InvoiceItems.append({

                                        "Item": ItemMapping[0]["id"],
                                        "Unit": MC_UnitID[0]["id"],
                                        "BatchCode": bb['BatchCode'],
                                        "Quantity":  bb['Quantity'],
                                        "BatchDate": BatchDate,
                                        "BaseUnitQuantity": 1,
                                        "LiveBatch": "",
                                        "MRP": "",
                                        "MRPValue": bb['MRP'],
                                        "Rate": bb['LandedPerUnitRate'],
                                        "BasicAmount": bb['TaxableAmount'],
                                        "GSTAmount": float(bb['CGST'])+float(bb['SGST'])+float(bb['IGST'])+float(bb['UGST']),
                                        "GST": "",
                                        "GSTPercentage": float(bb['CGSTPercentage'])+float(bb['SGSTPercentage'])+float(bb['IGSTPercentage'])+float(bb['UGSTPercentage']),
                                        "CGST": bb['CGST'],
                                        "SGST": bb['SGST'],
                                        "IGST": bb['IGST'],
                                        "CGSTPercentage": round(float(bb['CGSTPercentage']), 2),
                                        "SGSTPercentage": round(float(bb['CGSTPercentage']), 2),
                                        "IGSTPercentage": round(float(bb['IGSTPercentage']), 2),
                                        "Amount": bb['TotalValue'],
                                        "TaxType": 'GST',
                                        "DiscountType": 1,
                                        "LiveBatch": "",
                                        "Discount": bb['DiscountPercentage'],
                                        "DiscountAmount": bb['DiscountAmount'],

                                        'BaseUnitQuantity': round(BaseUnitQuantity, 3),

                                        "QtyInNo":  float(QtyInNo),
                                        "QtyInKg":  float(QtyInKg),
                                        "QtyInBox": float(QtyInBox)
                                    })

                                # CustomPrint(InvoiceItems)    
                                InvoiceData = list()
                                InvoiceData.append({

                                    "GrandTotal": aa['GrossAmount'],
                                    "RoundOffAmount": "0.00",
                                    "InvoiceNumber": 1,
                                    "FullInvoiceNumber": aa["InvoiceNumber"],
                                    "Customer": CustomerMapping[0]["id"],
                                    "Party": PartyMapping[0]["id"],
                                    "CreatedBy": 30,
                                    "UpdatedBy": 30,
                                    "TCSAmount" : aa['TCSAmount'], 
                                    "InvoiceDate": InvoiceDate,
                                    "InvoiceItems": InvoiceItems,
                                    "CustomerGSTIN": CustomerMapping[0]["GSTIN"]

                                })
                                # CustomPrint(InvoiceData[0])

                                Invoice_serializer = InvoiceSerializer(
                                    data=InvoiceData[0])
                                if Invoice_serializer.is_valid():
                                    Invoice_serializer.save()
                                    log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+ aa["InvoiceNumber"],292,0)
                                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully', 'Data': []})

                                else:
                                    log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceSave:'+ str(Invoice_serializer.errors),34,0)
                                    transaction.set_rollback(True)
                                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data': []})
                                    
                            
                            else:
                                log_entry = create_transaction_logNew(request, aa, 0, 'SAPInvoiceID:'+ aa["InvoiceNumber"],293,0)
                                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice already exist', 'Data': []})
                    
                    else:
                        # Invalid authorization header or authentication failed
                        return Response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'SAPInvoiceSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})


class SAPOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                OrderID = data["Order"]
                payload = list()
                Items =list()
                missing_units = [] 
                queryforcustomerID=T_Orders.objects.filter(id=OrderID).values('Customer')
                
                ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(queryforcustomerID[0]['Customer'],0).split('!')              
                
            # ===================================This code sends Deccan and Bajirao orders to SAP. The plantId should be replaced according to the Settings =============
                PlantID='0'
                cssOrdersendtosapcondition=M_Settings.objects.filter(id=67).values('DefaultValue') 
                SettingValues=cssOrdersendtosapcondition[0]['DefaultValue'].split(',')
                # b = SettingValues.split(',')
                for i in SettingValues:
                   c=i.split('-')
                   
                   if int(c[0]) == int(queryforcustomerID[0]['Customer']):
                        D=M_Parties.objects.filter(id=c[1]).values('SAPPartyCode')
                        PlantID=D[0]['SAPPartyCode']
                   
            #============================= 
                
                
                
                
                query=T_Orders.objects.raw(f'''select (5000000+T_Orders.id)id ,C.SAPPartyCode CustomerID,T_Orders.OrderDate DocDate,
                                           M_PartyType.SAPIndicator Indicator,
                TC_OrderItems.id ItemNo,M_Items.SAPItemCode Material,S.SAPPartyCode Plant,M_Units.SAPUnit Unit,
                (case when M_Items.SAPUnitID = 1 then TC_OrderItems.QtyInNo else TC_OrderItems.QtyInKg end)Quantity,M_Items.id ItemID,M_Items.Name ItemName,{ItemsGroupJoinsandOrderby[0]}

                from T_Orders 
                join TC_OrderItems on T_Orders.id=TC_OrderItems.Order_id
                join M_Parties S on S.id=T_Orders.Supplier_id
                join M_Parties C on C.id=T_Orders.Customer_id
                join M_PartyType on M_PartyType.id=C.PartyType_id
                join M_Items on M_Items.id=TC_OrderItems.Item_id
                left join M_Units on M_Units.id=M_Items.SAPUnitID
                {ItemsGroupJoinsandOrderby[1]}
                where IsDeleted = 0 AND T_Orders.id=%s {ItemsGroupJoinsandOrderby[2]}''',[OrderID])                
                # print(query)
                for row in query:
                    # print("Unit:{row.unit}")
                    if  row.Unit is None:
                        # return JsonResponse({'StatusCode': 204,'Status': True,'Message': f"Missing SAP Unit for SAPItemCode: {row.Material},ItemID:{row.ItemID} and ItemName:{row.ItemName}",'Data': []})
                        missing_units.append(f"SAPItemCode: {row.Material}, ItemID: {row.ItemID}, ItemName: {row.ItemName}")
                    date_obj = datetime.strptime(str(row.DocDate), '%Y-%m-%d')
                    Customer  =str(row.CustomerID)
                    
                    DocDate = date_obj.strftime('%d.%m.%Y')
                    Indicator = str(row.Indicator)
                    OrderNo = str(row.id)
                    Items.append({
                                            "OrderNo": str(row.id),
                                            "ItemNo": str(row.ItemNo),
                                            "Material": str(row.Material),
                                            "Quantity": str(round(row.Quantity,3)),
                                            "Unit": str(row.Unit),
                                            "Plant": str(PlantID) if str(PlantID) > '0' else str(row.Plant),
                                            "Batch": ""                                        
                                        })
                if missing_units:
                    message_text = "Missing SAP Unit for the following items:\n" + "\n".join(missing_units)

                    return JsonResponse({'StatusCode': 204,'Status': True,'Message': message_text,'Data': []
                    })

                payload.append({

                        "Customer": Customer,
                        "DocDate": DocDate,
                        "Indicator": Indicator,
                        "OrderNo": OrderNo,
                        "Stats": "1",
                        "CancelFlag": "",
                        "OrderItemSet": Items  

                })
                
                jsonbody=json.dumps(payload[0])
                
                # CustomPrint(jsonbody)
                SAPURL, Token  = GetThirdPartyAPIs(26)
                # url = "http://cbms4prdapp.chitalebandhu.net.in:8000/sap/opu/odata/sap/ZCBM_OD_SD_CSCMFOODERP_SRV/OrderHeaderSet"
                url = SAPURL
                headers = {
                    'X-Requested-With': 'x',
                    'Authorization': 'Basic SW50ZXJmYWNlOkFkbWluQDEyMzQ=',
                    'Content-Type': 'application/json',
                    'Cookie': 'SAP_SESSIONID_CSP_900=zUHoJ83NYxxPWHzOoQ8TsJOcV2HvGxHtptICAEHiAA8%3d; sap-usercontext=sap-client=900'
                }
                
                response = requests.request("POST", url, headers=headers, data=jsonbody)
                # Convert XML to OrderedDict
                data_dict = xmltodict.parse(response.text)
                # Convert OrderedDict to JSON string
                json_data = json.dumps(data_dict)
                # Convert JSON string to Python dictionary
                data_dict = json.loads(json_data)
                # CustomPrint(data_dict)
                a = str(data_dict)
                
                index = a.find('entry')

                if index != -1:
                    OrderID = int(OrderNo)-5000000
                    # CustomPrint(jsonbody)
                    aa = T_Orders.objects.filter(id=OrderID).update(
                        SAPResponse=data_dict['entry']['content']['m:properties']['d:Stats'])
                    log_entry = create_transaction_logNew(request, jsonbody, queryforcustomerID[0]['Customer'], OrderID,321,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Send Successfully ', 'Data': []})
                else:
                    index = a.find('error')
                    if index != -1:
                        log_entry = create_transaction_logNew(request, jsonbody,queryforcustomerID[0]['Customer'], 'SAPOrderSend:'+str(data_dict['error']['innererror']['errordetails']['errordetail'][0]['message']),322,0)
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': data_dict['error']['innererror']['errordetails']['errordetail'][0]['message'], 'Data': []})
                    else:
                        log_entry = create_transaction_logNew(request, jsonbody, queryforcustomerID[0]['Customer'], '',323,0)
                        return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Another exception raised from SAP', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'SAPOrderSend:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class SAPLedgerView(CreateAPIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request):
        SapLedgerdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = SapLedgerdata['FromDate']
                ToDate = SapLedgerdata['ToDate']
                SAPCode = SapLedgerdata['SAPCode']

            OpeningBalanceDate = '2025-04-01'
            opening_balance = 0.0

            if FromDate == OpeningBalanceDate:
                # Only use 'O' entry
                opening_balance = M_SAPCustomerLedger.objects.filter(CustomerCode=SAPCode,DebitCredit='O',FileDate=OpeningBalanceDate).aggregate(total=Sum('Amount'))['total'] or 0.0

            elif FromDate > OpeningBalanceDate:
                # Get opening balance from 1-April 'O' entry
                opening_balance = M_SAPCustomerLedger.objects.filter(CustomerCode=SAPCode,DebitCredit='O',FileDate=OpeningBalanceDate).aggregate(total=Sum('Amount'))['total'] or 0.0

                # Sum of credits and debits from 1-April to (FromDate-1)
                day_before = (datetime.strptime(FromDate, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                transactions = M_SAPCustomerLedger.objects.filter(FileDate__range=[OpeningBalanceDate, day_before],CustomerCode=SAPCode).exclude(DebitCredit='O')

                total_credit = transactions.filter(DebitCredit='H').aggregate(total=Sum('Amount'))['total'] or 0.0
                total_debit = transactions.filter(DebitCredit='S').aggregate(total=Sum('Amount'))['total'] or 0.0

                opening_balance = opening_balance + total_credit - total_debit

            # Now fetch transactions in given date range
            queryset = M_SAPCustomerLedger.objects.filter(FileDate__range=[FromDate, ToDate],CustomerCode=SAPCode
                        ).exclude(DebitCredit='O').values('CompanyCode', 'DocumentDesc', 'CustomerCode', 'CustomerName',
                        'DocumentNo','FiscalYear', 'DebitCredit', 'Amount', 'DocumentType','PostingDate', 'ItemText').order_by('PostingDate')

            if queryset.exists():
                ledger_data = []
                total_credit = 0.0
                total_debit = 0.0
                
                balance = opening_balance  # initialize running balance with opening balance

                for row in queryset:
                    amount = row['Amount']
                    debit_amount = 0.0
                    credit_amount = 0.0

                    if row['DebitCredit'] == 'H':
                        credit_amount = amount
                        total_credit += amount
                        balance += credit_amount 
                    elif row['DebitCredit'] == 'S':
                        debit_amount = amount
                        total_debit += amount
                        balance -= debit_amount 

                    ledger_data.append({
                        "CompanyCode": row['CompanyCode'],
                        "DocumentDesc": row['DocumentDesc'],
                        "CustomerNumber": row['CustomerCode'],
                        "CustomerName": row['CustomerName'],
                        "DocumentNo": row['DocumentNo'],
                        "Fiscalyear": row['FiscalYear'],
                        "DebitCredit": row['DebitCredit'],
                        "Amount": round(amount, 2),
                        "DocumentType": row['DocumentType'],
                        "PostingDate": row['PostingDate'].strftime('%d/%m/%Y %I:%M:%S %p'),
                        "ItemText": row['ItemText'],
                        "Debit": round(debit_amount, 2),
                        "Credit": round(credit_amount, 2),
                        "Balance": round(balance, 2) 
                    })

                count = len(ledger_data)
                closing_balance = opening_balance + total_credit - total_debit

                log_entry = create_transaction_logNew(request, SapLedgerdata, SAPCode, f'OpeningBal:{opening_balance} ClosingBal: {closing_balance}', 324, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 200,"Status": True,"Message": "",
                                     "Data": {"status": True,"status_code": 200,"count": count,"OpeningBal": round(opening_balance, 2),"ClosingBal": round(closing_balance, 2),"data": ledger_data}})
            else:
                log_entry = create_transaction_logNew(request, SapLedgerdata, SAPCode, 'SAPLedger: Data Not Found', 324, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, SapLedgerdata, SAPCode, 'SAPLedger: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})


# class SAPLedgerView(CreateAPIView):
#     permission_classes = ()

#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 SapLedgerdata = JSONParser().parse(request)
#                 FromDate = SapLedgerdata['FromDate']
#                 ToDate = SapLedgerdata['ToDate']
#                 SAPCode = SapLedgerdata['SAPCode']

#                 payload = ""

#                 url = f'http://web.chitalebandhu.in:8080/FoodERPWebAPIPOS/api/SAPDataSendToSCM/GetSAPCustomerLedgerList?FromDate={FromDate}&ToDate={ToDate}&SAPCode={SAPCode}'

#                 headers = {}

#                 response = requests.request(
#                     "GET", url, headers=headers, data=payload)
#                 response_json = json.loads(response.text)
#                 # Convert XML to OrderedDict
#                 # data_dict = xmltodict.parse(response.text)
#                 # Convert OrderedDict to JSON string
#                 # json_data = json.dumps(data_dict)
#                 # # Convert JSON string to Python dictionary
#                 # data_dict = json.loads(json_data)
  
#                 if response_json:
#                     log_entry = create_transaction_logNew(request, SapLedgerdata, 0,'From:'+str(FromDate)+','+'To:'+str(ToDate)+','+'SAPCode:'+str(SAPCode),324,0,FromDate,ToDate,0)
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_json})       
#                 else:
#                     log_entry = create_transaction_logNew(request, SapLedgerdata, 0, 'SAPLedger:'+'SAPLedger Data Not Found',324,0)
#                     return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})               
#         except Exception as e:
#             log_entry = create_transaction_logNew(request, 0, 0, 'SAPLedger:'+str(e),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
        
class InvoiceToSCMView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Reportdata = JSONParser().parse(request)
                InvoiceID = Reportdata['Invoice']
               
                q1 = TC_InvoiceItems.objects.filter(Invoice =InvoiceID)
                LineItemsQuantity=q1.count()
          
                query = T_Invoices.objects.raw('''SELECT  T_Invoices.id,T_Invoices.InvoiceDate,TC_InvoicesReferences.Order_id as OrderNumber,(case when b.SAPPartyCode is null then b.id else b.SAPPartyCode end)  AS CustomerID,'' DriverName,'' VehicleNo,b.GSTIN,a.SAPPartyCode as Plant,T_Invoices.GrandTotal GrossAmount,'' refInvoiceNo,'' refInvoiceType, '' refInvoiceDate,'' AS LineItemsQuantity,M_Items.SAPItemCode AS MaterialCode,BatchCode,BatchDate,TC_InvoiceItems.QtyInNo,'' BaseUOM, Rate as LandedPerUnitRate,MRPValue as MRP, BasicAmount as TaxableAmount,CGST,SGST,IGST,'' UGST,CGSTPercentage, SGSTPercentage, IGSTPercentage, '' UGSTPercentage,Discount as DiscountPercentage, DiscountAmount,Amount as TotalValue FROM T_Invoices LEFT JOIN TC_InvoicesReferences ON TC_InvoicesReferences.Invoice_id=T_Invoices.id JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id JOIN M_Parties a ON a.id=T_Invoices.Party_id JOIN M_Parties b ON b.id=T_Invoices.Customer_id  JOIN M_Items ON M_Items.id=TC_InvoiceItems.Item_id  Where T_Invoices.id=%s ''',[InvoiceID])
                if query:
                   
                    InvoiceSCMSerializer=InvoiceToSCMSerializer(query, many=True).data
                    Invoicedate = datetime.strptime(InvoiceSCMSerializer[0]['InvoiceDate'], "%Y-%m-%d")
                    Invoiceformatted_date = Invoicedate.strftime("%d.%m.%Y")
                    InvoiceData = list()
                    InvoiceItemData = list()
                    for a in InvoiceSCMSerializer:
                        parsed_date = datetime.strptime(a['BatchDate'], "%Y-%m-%d")
                        formatted_date = parsed_date.strftime("%d.%m.%Y")
                       
                        InvoiceItemData.append({
                            "InvoiceNumber":'80000'+str(a['id']),
                            "MaterialCode":a['MaterialCode'],
                            "BatchCode":a['BatchCode'],
                            "BatchDate":formatted_date,
                            "Quantity":a['QtyInNo'],
                            "BaseUOM":"EA",
                            "LandedPerUnitRate":a['LandedPerUnitRate'],
                            "MRP":a['MRP'],
                            "TaxableAmount":a['TaxableAmount'],
                            "CGST":a['CGST'],
                            "SGST":a['SGST'],
                            "IGST":a['IGST'],
                            "UGST":"0.00",
                            "CGSTPercentage":a['CGSTPercentage'],
                            "SGSTPercentage":a['SGSTPercentage'],
                            "IGSTPercentage":a['IGSTPercentage'],
                            "UGSTPercentage":"0",
                            "DiscountAmount":a['DiscountAmount'],
                            "DiscountPercentage":a['DiscountPercentage'],
                            "TotalValue":a['TotalValue'],
                        })
                   
                    InvoiceData.append({
                            "Reference":"",
                            "InvoiceNumber":'80000'+str(InvoiceSCMSerializer[0]['id']),
                            "InvoiceDate":Invoiceformatted_date,
                            "OrderNumber":'80000'+str(InvoiceSCMSerializer[0]['id']),
                            "CustomerID":InvoiceSCMSerializer[0]['CustomerID'],
                            "DriverName":"",
                            "VehicleNo":"",
                            "GSTIN":InvoiceSCMSerializer[0]['GSTIN'],
                            "Plant":InvoiceSCMSerializer[0]['Plant'],
                            "GrossAmount":InvoiceSCMSerializer[0]['GrossAmount'],
                            "refInvoiceNo":InvoiceSCMSerializer[0]['refInvoiceNo'],
                            "refInvoiceType":InvoiceSCMSerializer[0]['refInvoiceType'],
                            "refInvoiceDate":InvoiceSCMSerializer[0]['refInvoiceDate'],
                            "LineItems":LineItemsQuantity,
                            "InvoiceItems":InvoiceItemData
                            
                            })
                    
                    # return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'' , 'Data':InvoiceData[0]}) 
                    SAPURL, Token  = GetThirdPartyAPIs(27)  
                    # url = "https://cfe.chitalegroup.co.in/chitalescm/RestAPI/RestController.php?page_key=GetSAPInvoice"           
                    url = SAPURL
                    payload = json.dumps(InvoiceData[0])
                    headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Basic YXR0cmliOkF0dHJpYkA5OTk='
                    }
                   
                    response = requests.request("POST", url, headers=headers, data=payload)
                    corrected_response_text = '[' + response.text.replace('Array', '') + ']'
                    response_json = json.loads(corrected_response_text)
                    # CustomPrint(response_json[0]['Status'])
                    # CustomPrint(response_json[0]['Messag'])
                    
                    if (response_json[0]['Status']== False):
                        Msg = response_json[0]['Messag']
                        log_entry = create_transaction_logNew(request, Reportdata, 0, 'False Status In Response While Invoice Send to SCM ',325,0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':Msg, 'Data':payload })  
                    else:
                        Msg = response_json[0]['Messag']
                        log_entry = create_transaction_logNew(request, Reportdata, 0, '',325,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': Msg, 'Data': payload})    
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'SAPInvoice Not Send To SCM',325,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Invoice Not Send', 'Data': payload})  
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'InvoiceToSCM:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':payload})        
