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

class ChallanView(CreateAPIView):
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
                for b in GRN_serializer['GRNItems']:
                    GRNItemListData.append({
                        "Item": b['Item']['id'],
                        "ItemName": b['Item']['Name'],
                        "Quantity": b['Quantity'],
                        "Unit": b['Unit']['id'],
                        "UnitName": b['Unit']['BaseUnitConversion'],
                        "BaseUnitQuantity": b['BaseUnitQuantity'],
                        "MRP": b['MRP'],
                        "ReferenceRate": b['ReferenceRate'],
                        "Rate": b['Rate'],
                        "BasicAmount": b['BasicAmount'],
                        "TaxType": b['TaxType'],
                        "GST": b['GST']['id'],
                        "GSTPercentage": b['GST']['GSTPercentage'],
                        "HSNCode": b['GST']['HSNCode'],
                        "GSTAmount": b['GSTAmount'],
                        "Amount": b['Amount'],
                        "DiscountType": b['DiscountType'],
                        "Discount": b['Discount'],
                        "DiscountAmount": b['DiscountAmount'],
                        "CGST": b['CGST'],
                        "SGST": b['SGST'],
                        "IGST": b['IGST'],
                        "CGSTPercentage": b['CGSTPercentage'],
                        "SGSTPercentage": b['SGSTPercentage'],
                        "IGSTPercentage": b['IGSTPercentage'],
                        "BatchDate": b['BatchDate'],
                        "BatchCode": b['BatchCode'],
                        "SystemBatchDate": b['SystemBatchDate'],
                        "SystemBatchCode": b['SystemBatchCode'],                            
                    })
                GRNListData = list()
                a = GRN_serializer
                GRNListData.append({
                    "GRN": a['id'],
                    "ChallanDate": a['GRNDate'],
                    "Party": a['Customer']['id'],
                    "PartyName": a['Customer']['Name'],
                    "GrandTotal": a['GrandTotal'],
                    "Customer": a['Party']['id'],
                    "CustomerName": a['Party']['Name'],
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


class ChallanListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Challandata = JSONParser().parse(request)
                FromDate = Challandata['FromDate']
                ToDate = Challandata['ToDate']
                Customer = Challandata['Customer']
                Party = Challandata['Party']
                if(Customer == ''):
                    query = T_Challan.objects.filter(ChallanDate__range=[FromDate, ToDate], Party=Party)
                else:
                    query = T_Challan.objects.filter(ChallanDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Party) 
                    
                if query:
                    Challan_serializer = ChallanSerializerList(query, many=True).data
                    ChallanListData = list()
                    for a in Challan_serializer:
                        ChallanListData.append({
                            "id": a['id'],
                            "ChallanDate": a['ChallanDate'],
                            "FullChallanNumber": a['FullChallanNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "CreatedOn": a['CreatedOn'] 
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ChallanListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        