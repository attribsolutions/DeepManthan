import base64
import datetime
import json
from time import strftime
from django.contrib.auth import authenticate
from base64 import b64decode
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.db import transaction

from ..Serializer.S_SAPApi import InvoiceSerializer
from ..Serializer.S_Orders import *
from ..models import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
import requests
import xml.etree.ElementTree as ET
import xmltodict
import json


class SAPInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                
                aa = JSONParser().parse(request)
                log_entry = create_transaction_log(request, aa, 0, 0, "initial")
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                # print(auth_header)
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

                        DuplicateCheck = T_Invoices.objects.filter(
                            FullInvoiceNumber=aa["InvoiceNumber"])
                        if(DuplicateCheck.count() == 0):
                                
                               
                            CustomerMapping = M_Parties.objects.filter(
                                SAPPartyCode=aa['CustomerID']).values("id")
                            PartyMapping = M_Parties.objects.filter(
                                SAPPartyCode=aa['Plant']).values("id")

                            if CustomerMapping.exists():
                                aa['Customer'] = CustomerMapping
                            else:
                                log_entry = create_transaction_log(request, aa, 0, 0, 'Invalid Customer Data ')
                                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Customer Data ", 'Data': []})
                            
                            if PartyMapping.exists():
                                aa['Party'] = PartyMapping
                            else:
                                log_entry = create_transaction_log(request, aa, 0, 0, 'Invalid Plant Data ')
                                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Plant Data ", 'Data': []})

                            InvoiceDate = datetime.datetime.strptime(
                                aa['InvoiceDate'], "%d.%m.%Y").strftime("%Y-%m-%d")
                            for bb in aa['InvoiceItems']:

                                ItemMapping = M_Items.objects.filter(
                                    SAPItemCode=bb['MaterialCode']).values("id")
                                UnitMapping = M_Units.objects.filter(
                                    SAPUnit=bb['BaseUOM']).values("id")
                                # print(ItemMapping,UnitMapping)
                               
                                if ItemMapping.exists():
                                    bb['Item'] = ItemMapping
                                else:
                                    log_entry = create_transaction_log(request, aa, 0, 0, 'Invalid Material Code')
                                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Material Code", 'Data': []})

                                if UnitMapping.exists():

                                    MC_UnitID = MC_ItemUnits.objects.filter(
                                        UnitID=UnitMapping[0]["id"], Item=ItemMapping[0]["id"], IsDeleted=0).values("id")
                                    # print(MC_UnitID)

                                    if MC_UnitID.exists():
                                        bb['Unit'] = MC_UnitID
                                    else:
                                        log_entry = create_transaction_log(request, aa, 0, 0, 'Invalid Material Code')
                                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Item Unit  ", 'Data': []})
                                else:
                                    log_entry = create_transaction_log(request, aa, 0, 0, 'Invalid Unit Code')
                                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Unit", 'Data': []})

                                BaseUnitQuantity = UnitwiseQuantityConversion(
                                    ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 0, 0).GetBaseUnitQuantity()
                                QtyInNo = UnitwiseQuantityConversion(
                                    ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 1, 0).ConvertintoSelectedUnit()
                                QtyInKg = UnitwiseQuantityConversion(
                                    ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 2, 0).ConvertintoSelectedUnit()
                                QtyInBox = UnitwiseQuantityConversion(
                                    ItemMapping[0]["id"], bb['Quantity'], MC_UnitID[0]["id"], 0, 0, 4, 0).ConvertintoSelectedUnit()
                                
                                InvoiceItems.append({

                                    "Item": ItemMapping[0]["id"],
                                    "Unit": MC_UnitID[0]["id"],
                                    "BatchCode": bb['BatchCode'],
                                    "Quantity":  bb['Quantity'],
                                    "BatchDate": InvoiceDate,
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

                            # print(InvoiceItems)    
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
                                "TCSAmount" : 0, 
                                "InvoiceDate": InvoiceDate,
                                "InvoiceItems": InvoiceItems

                            })
                            # print(InvoiceData[0])

                            Invoice_serializer = InvoiceSerializer(
                                data=InvoiceData[0])
                            if Invoice_serializer.is_valid():
                                Invoice_serializer.save()
                                log_entry = create_transaction_log(request, aa, 0, 0, aa["InvoiceNumber"]+" Invoice Save Successfully")
                                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully', 'Data': []})

                            else:
                                transaction.set_rollback(True)
                                log_entry = create_transaction_log(
                                    request, aa, 0, 0, Invoice_serializer.errors)
                                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data': []})
                                
                        
                        else:
                            log_entry = create_transaction_log(request, aa, 0, 0, 'Invoice already exist')
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice already exist', 'Data': []})
                    else:
                        # Invalid authorization header or authentication failed
                        return Response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})


class SAPOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                log_entry = create_transaction_log(request, data, 0, 0, "initiat")
                payload = json.dumps(data)
                print('aaaaaaaa')
                url = "http://cbms4prdapp.chitalebandhu.net.in:8000/sap/opu/odata/sap/ZCBM_OD_SD_CSCMFOODERP_SRV/OrderHeaderSet"

                headers = {
                    'X-Requested-With': 'x',
                    'Authorization': 'Basic SW50ZXJmYWNlOkFkbWluQDEyMzQ=',
                    'Content-Type': 'application/json',
                    'Cookie': 'SAP_SESSIONID_CSP_900=zUHoJ83NYxxPWHzOoQ8TsJOcV2HvGxHtptICAEHiAA8%3d; sap-usercontext=sap-client=900'
                }
                print('bbbbb')
                response = requests.request(
                    "POST", url, headers=headers, data=payload)
                # Convert XML to OrderedDict
                data_dict = xmltodict.parse(response.text)
                # Convert OrderedDict to JSON string
                json_data = json.dumps(data_dict)
                # Convert JSON string to Python dictionary
                data_dict = json.loads(json_data)
                # print(data_dict)
                a = str(data_dict)
                index = a.find('entry')

                if index != -1:
                    OrderID = int(data['OrderNo'])-5000000
                    aa = T_Orders.objects.filter(id=OrderID).update(
                        SAPResponse=data_dict['entry']['content']['m:properties']['d:Stats'])
                    log_entry = create_transaction_log(request, data, 0, 0, data_dict['entry']['content']['m:properties']['d:Stats'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Send Successfully ', 'Data': []})
                else:
                    index = a.find('error')
                    if index != -1:
                        log_entry = create_transaction_log(request, data, 0, 0, data_dict['error']['innererror']['errordetails']['errordetail'][0]['message'])
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': data_dict['error']['innererror']['errordetails']['errordetail'][0]['message'], 'Data': []})
                    else:
                        log_entry = create_transaction_log(request, data, 0, 0, 'Another exception raised from SAP')
                        return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Another exception raised from SAP', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class SAPLedgerView(CreateAPIView):
    permission_classes = ()

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                SapLedgerdata = JSONParser().parse(request)
                FromDate = SapLedgerdata['FromDate']
                ToDate = SapLedgerdata['ToDate']
                SAPCode = SapLedgerdata['SAPCode']

                payload = ""

                url = f'http://web.chitalebandhu.in:8080/FoodERPWebAPIPOS/api/SAPDataSendToSCM/GetSAPCustomerLedgerList?FromDate={FromDate}&ToDate={ToDate}&SAPCode={SAPCode}'

                headers = {}

                response = requests.request(
                    "GET", url, headers=headers, data=payload)
                response_json = json.loads(response.text)
                # Convert XML to OrderedDict
                # data_dict = xmltodict.parse(response.text)
                # Convert OrderedDict to JSON string
                # json_data = json.dumps(data_dict)
                # # Convert JSON string to Python dictionary
                # data_dict = json.loads(json_data)

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_json})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
