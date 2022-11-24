from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_DeliveryChallans import *
from ..Views.V_TransactionNumberfun import GetMaxNumber,GetPrifix

from ..models import  *



class DeliveryChallanListFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                DeliveryChallandata = JSONParser().parse(request)
                FromDate = DeliveryChallandata['FromDate']
                ToDate = DeliveryChallandata['ToDate']
                Customer = DeliveryChallandata['Party']
                Supplier = DeliveryChallandata['Supplier']
                if(Supplier==''):
                    query = T_DeliveryChallans.objects.filter(ChallanDate__range=[FromDate,ToDate],Customer_id=Customer)
                else:
                    query = T_DeliveryChallans.objects.filter(ChallanDate__range=[FromDate,ToDate],Customer_id=Customer,Party_id=Supplier)    
                # return JsonResponse({'Data':str(query.query)})
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})
                else:
                    DeliveryChallan_serializer = T_DeliveryChallanSerializerForGET(query, many=True).data
                    ChallanListData = list()
                    for a in DeliveryChallan_serializer:   
                        ChallanListData.append({
                        "id": a['id'],
                        "ChallanDate": a['ChallanDate'],
                        "Customer": a['Customer']['id'],
                        "CustomerName": a['Customer']['Name'],
                        "ChallanNumber": a['ChallanNumber'],
                        "FullChallanNumber": a['FullChallanNumber'],
                        "GrandTotal": a['GrandTotal'],
                        "Party": a['Party']['id'],
                        "PartyName": a['Party']['Name'],
                        "CreatedBy":a['CreatedBy'],
                        "UpdatedBy": a['UpdatedBy'],

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ChallanListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class T_DeliveryChallanView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                DeliveryChallandata = JSONParser().parse(request)
                Customer = DeliveryChallandata['Customer']
                '''Get Max DeliveryChallan Number'''
                a=GetMaxNumber.GetDeliveryChallanNumber(Customer)
                # return JsonResponse({'Data':a})
                DeliveryChallandata['ChallanNumber']= a
                '''Get DeliveryChallan Prifix '''
                b=GetPrifix.GetDeliveryChallanPrifix(Customer)
                # return JsonResponse({'Data':b})
                DeliveryChallandata['FullChallanNumber']= b+""+str(a)
                DeliveryChallandata_serializer = T_DeliveryChallanSerializer(data=DeliveryChallandata)
                if DeliveryChallandata_serializer.is_valid():
                    DeliveryChallandata_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': 'Delivery Challan Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': DeliveryChallandata_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class T_DeliveryChallanViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
        
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                DeliveryChallandata = T_DeliveryChallans.objects.get(id=id)
                DeliveryChallan_serializer = T_DeliveryChallanSerializerForGET(DeliveryChallandata).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRN_serializer})
                ChallanItemListData = list()
                for a in DeliveryChallan_serializer['DeliveryChallanItems']:   
                        ChallanItemListData.append({
                        "Item": a['Item']['id'],
                        "ItemName":a['Item']['Name'],
                        "Quantity": a['Quantity'],
                        "Unit" :a['Unit']['id'],    
                        "UnitName" :a['Unit']['UnitID'],    
                        "BaseUnitQuantity": a['BaseUnitQuantity'],
                        "MRP": a['MRP'],
                        "ReferenceRate": a['ReferenceRate'],
                        "Rate": a['Rate'],
                        "BasicAmount": a['BasicAmount'],
                        "TaxType": a['TaxType'],
                        "GSTPercentage": a['GSTPercentage'],
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
                    })

                ChallanReferencesData = list()
                for r in DeliveryChallan_serializer['DeliveryChallanReferences']:   
                        ChallanReferencesData.append({
                            "GRN": r['GRN']
                        })
                            
                ChallanListData = list()
                a=DeliveryChallan_serializer
                ChallanListData.append({
                    "id": a['id'],
                    "ChallanDate": a['ChallanDate'],
                    "Customer": a['Customer']['id'],
                    "CustomerName": a['Customer']['Name'],
                    "ChallanNumber": a['ChallanNumber'],
                    "FullChallanNumber": a['FullChallanNumber'],
                    "GrandTotal": a['GrandTotal'],
                    "Party": a['Party']['id'],
                    "PartyName": a['Party']['Name'],
                    "CreatedBy": a['CreatedBy'],
                    "UpdatedBy": a['UpdatedBy'],
                    "DeliveryChallanReferences": ChallanReferencesData,
                    "DeliveryChallanItems" : ChallanItemListData  
                    })  
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ChallanListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                DeliveryChallandata = JSONParser().parse(request)
                DeliveryChallanByID = T_DeliveryChallans.objects.get(id=id)
                DeliveryChallan_Serializer = T_DeliveryChallanSerializer(DeliveryChallanByID, data=DeliveryChallandata)
                if DeliveryChallan_Serializer.is_valid():
                    DeliveryChallan_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Delivery Challan Updated Successfully','Data':{}})
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': DeliveryChallan_Serializer.errors ,'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                DeliveryChallan_Data = T_DeliveryChallans.objects.get(id=id)
                DeliveryChallan_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Message': 'Delivery Challan Deleted Successfully', 'Data':[]})
        except T_DeliveryChallans.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Delivery Challan used in another tbale', 'Data': []})    


