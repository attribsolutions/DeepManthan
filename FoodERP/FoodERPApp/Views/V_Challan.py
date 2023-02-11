from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GRNs import *
from ..Serializer.S_Challan import *
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..models import  *

class VDCChallanViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                GRNdata = T_GRNs.objects.get(id=id)
                GRN_serializer = T_GRNSerializerForGETSecond(GRNdata).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRN_serializer})
                GRNItemListData = list()
                for a in GRN_serializer['GRNItems']:
                    GRNItemListData.append({
                        "Item": a['Item']['id'],
                        "ItemName": a['Item']['Name'],
                        "Quantity": a['Quantity'],
                        "Unit": a['Unit']['id'],
                        "UnitName": a['Unit']['BaseUnitConversion'],
                        "BaseUnitQuantity": a['BaseUnitQuantity'],
                        "MRP": a['MRP'],
                        "ReferenceRate": a['ReferenceRate'],
                        "Rate": a['Rate'],
                        "BasicAmount": a['BasicAmount'],
                        "TaxType": a['TaxType'],
                        "GST": a['GST']['id'],
                        "GSTPercentage": a['GST']['GSTPercentage'],
                        "HSNCode": a['GST']['HSNCode'],
                        "GSTAmount": a['GSTAmount'],
                        "Amount": a['Amount'],
                        "DiscountType": a['DiscountType'],
                        "Discount": a['Discount'],
                        "DiscountAmount": a['DiscountAmount'],
                        "CGST": a['CGST'],
                        "SGST": a['SGST'],
                        "IGST": a['IGST'],
                        "CGSTPercentage": a['CGSTPercentage'],
                        "SGSTPercentage": a['SGSTPercentage'],
                        "IGSTPercentage": a['IGSTPercentage'],
                        "BatchDate": a['BatchDate'],
                        "BatchCode": a['BatchCode'],
                        "SystemBatchDate": a['SystemBatchDate'],
                        "SystemBatchCode": a['SystemBatchCode'],
                                                
                    })

                GRNListData = list()
                a = GRN_serializer
                GRNListData.append({
                    "GRN": a['id'],
                    "ChallanDate": a['GRNDate'],
                    "Customer": a['Customer']['id'],
                    "CustomerName": a['Customer']['Name'],
                    "GrandTotal": a['GrandTotal'],
                    "Party": a['Party']['id'],
                    "PartyName": a['Party']['Name'],
                    "CreatedBy": a['CreatedBy'],
                    "UpdatedBy": a['UpdatedBy'],
                    "RoundOffAmount":"",
                    "ChallanItems": GRNItemListData,
                    "BatchWiseLiveStockGRNID":a['BatchWiseLiveStockGRNID']
                })
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]})
                Party = GRNListData[0]['Party']
                ChallanDate = GRNListData[0]['ChallanDate']
                # ==========================Get Max Invoice Number=====================================================
                a = GetMaxNumber.GetChallanNumber(Party,ChallanDate)
                GRNListData[0]['ChallanNumber'] = a
                b = GetPrifix.GetChallanPrifix(Party)
                GRNListData[0]['FullChallanNumber'] = str(b)+""+str(a)
                #==================================================================================================
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]}) 
                Challan_serializer = ChallanSerializer(data=GRNListData[0])
                if Challan_serializer.is_valid():
                    # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.data, 'Data':[]})
                    Challan_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Challan Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Challan_data = T_Challan.objects.get(id=id)
                Challan_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Challan Deleted Successfully','Data':[]})
        except T_Challan.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Challan Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Challan used in another table', 'Data': []})