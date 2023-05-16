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
import requests



class SAPInvoiceView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                aa = JSONParser().parse(request)
                
                CustomerMapping=M_Parties.objects.filter(SAPPartyCode=aa['CustomerID']).values("id")
                PartyMapping=M_Parties.objects.filter(SAPPartyCode=aa['Plant']).values("id")
                print(CustomerMapping,PartyMapping)
                if CustomerMapping.exists:
                        aa['Customer']=CustomerMapping
                else:
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Customer Data ", 'Data':[]})    
                if PartyMapping.exists:
                        aa['Party']=PartyMapping
                else:
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Customer Data ", 'Data':[]})    
                        
                for bb in aa['InvoiceItems']:
                    
                    ItemMapping=M_Items.objects.filter(SAPItemCode=bb['MaterialCode']).values("id")
                    UnitMapping=M_Units.objects.filter(SAPUnit=bb['BaseUOM']).values("id")
                    print(ItemMapping,UnitMapping)
                    InvoiceItems=list()
                    if ItemMapping.exists:
                        bb['Item']=ItemMapping
                    else:
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Material Code", 'Data':[]})     
                    
                    if UnitMapping.exists:
                        print('sssssssssssssssssssssss')
                        MC_UnitID=MC_ItemUnits.objects.filter(UnitID=UnitMapping[0]["id"],Item=ItemMapping[0]["id"],IsDeleted=0).values("id")
                        print(MC_UnitID)
                        
                        if MC_UnitID.exists():
                            bb['Unit']=MC_UnitID
                        else:
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid MC_ItemUnits ", 'Data':[]})            
                    else:
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Unit", 'Data':[]})
                    
                    InvoiceItems.append({
                                    
                                "Item": ItemMapping[0]["id"],
                                "Unit": MC_UnitID[0]["id"],
                                "BatchCode": bb['BatchCode'],
                                "Quantity":  bb['Quantity'],
                                "BatchDate": aa['InvoiceDate'],
                                "BaseUnitQuantity":1,
                                "LiveBatch": "",
                                "MRP": "",
                                "MRPValue":bb['MRP'],
                                "Rate": bb['LandedPerUnitRate'],
                                "BasicAmount": bb['TaxableAmount'],
                                "GSTAmount": float(bb['CGST'])+float(bb['SGST'])+float(bb['IGST'])+float(bb['UGST']),
                                "GST": "",
                                "GSTPercentage": float(bb['CGSTPercentage'])+float(bb['SGSTPercentage'])+float(bb['IGSTPercentage'])+float(bb['UGSTPercentage']),
                                "CGST": bb['CGST'],
                                "SGST":bb['SGST'],
                                "IGST": bb['IGST'],
                                "CGSTPercentage": bb['CGSTPercentage'],
                                "SGSTPercentage": bb['SGSTPercentage'],
                                "IGSTPercentage": bb['IGSTPercentage'],
                                "Amount": bb['TotalValue'],
                                "TaxType":'GST',
                                "DiscountType":1,
                                "LiveBatch":"",
                                "Discount":bb['DiscountPercentage'],
                                "DiscountAmount":bb['DiscountAmount'],
                        })
                    InvoiceData=list()
                    InvoiceData.append({
                            
                            "GrandTotal":aa['GrossAmount'],
                            "RoundOffAmount": "0.00",
                            "InvoiceNumber": 1,
                            "FullInvoiceNumber": aa["InvoiceNumber"],
                            "Customer": CustomerMapping[0]["id"],
                            "Party": PartyMapping[0]["id"],
                            "CreatedBy": 30,
                            "UpdatedBy": 30,
                           
                            "InvoiceDate": aa['InvoiceDate'],
                            "InvoiceItems": InvoiceItems

                    })   
                    print(InvoiceData[0])
                   
                    Invoice_serializer = InvoiceSerializer(data=InvoiceData[0])
                    if Invoice_serializer.is_valid():
                        Invoice_serializer.save()
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data': []})
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully', 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})
        
         
class SAPOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                payload = JSONParser().parse(request)
                url = "http://cbms4prdapp.chitalebandhu.net.in:8000/sap/opu/odata/sap/ZCBM_OD_SD_CSCMFOODERP_SRV/OrderHeaderSet"


                headers = {
                    'X-Requested-With': 'x',
                    'Authorization': 'Basic SW50ZXJmYWNlOkFkbWluQDEyMzQ=',
                    'Content-Type': 'application/json',
                    'Cookie': 'SAP_SESSIONID_CSP_900=zUHoJ83NYxxPWHzOoQ8TsJOcV2HvGxHtptICAEHiAA8%3d; sap-usercontext=sap-client=900'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Send to SAP Successfully ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
              
          
    # authentication__Class = JSONWebTokenAuthentication

    # def get(self, request, id=0):
    #     try:
    #         with transaction.atomic():
    #             OrderQuery = T_Orders.objects.filter(id=id)
    #             if OrderQuery.exists():
    #                 OrderSerializedata = T_OrderSerializerThird(OrderQuery, many=True).data
    #                 OrderData = list()
    #                 for a in OrderSerializedata:
    #                     CustomerMapping=M_Parties.objects.filter(id=a['Customer']['id']).values("SAPPartyCode")
    #                     PartyMapping=M_Parties.objects.filter(id=a['Supplier']['id']).values("SAPPartyCode")
    #                     if CustomerMapping.exists:
    #                         CustomerSAPCode=CustomerMapping
    #                     else:
    #                         return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Customer Data ", 'Data':[]})    
    #                     if PartyMapping.exists:
    #                         Plant=PartyMapping
    #                     else:
    #                         return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Customer Data ", 'Data':[]})
                        
    #                     OrderItemSetDetails = list()
                    
    #                     for b in a['OrderItem']:
    #                         ItemMapping = M_Items.objects.filter(id=b['Item']['id']).values('SAPItemCode')
    #                         if ItemMapping.exists:
    #                             SAPItemCode = ItemMapping
    #                         else:
    #                             return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Material Code", 'Data': []})
    #                         MC_UnitID = MC_ItemUnits.objects.filter(id=b['Unit']['id']).values("UnitID")
    #                         UnitMapping = M_Units.objects.filter(id=MC_UnitID).values("SAPUnit")
    #                         if UnitMapping.exists:
    #                             Unit = UnitMapping
    #                         else:
    #                             return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Invalid Material Code", 'Data': []})

    #                         OrderItemSetDetails.append({
    #                             "OrderNo":b['Order_id'],
    #                             "ItemNo":b['id'] ,
    #                             "Material":SAPItemCode,
    #                             "Quantity": b['Quantity'],
    #                             "Unit": Unit,
    #                             "Plant": Plant,
    #                             "Batch": "",
    #                             "CancelFlag":""  
    #                         })

    #                     OrderData.append({
    #                         "Customer": CustomerSAPCode,
    #                         "DocDate": a['OrderDate'],
    #                         "Indicator": "F",
    #                         "OrderNo": a['id'],
    #                         "Stats": "1",
    #                         "OrderItemSet": OrderItemSetDetails,
    #                     })
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData[0]})
                             
                



