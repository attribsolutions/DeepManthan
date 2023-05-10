from django.contrib.auth import authenticate
from base64 import b64decode
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.db import transaction

from ..Serializer.S_SAPApi import InvoiceSerializer
from ..models import *

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





