from typing import Concatenate
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Demands import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *
from ..Serializer.S_Bom import *
from django.db.models import Sum
from ..models import *


class DemandListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Demanddata = JSONParser().parse(request)
                FromDate = Demanddata['FromDate']
                ToDate = Demanddata['ToDate']
                Customer = Demanddata['Customer'] # Customer Compansary
                Supplier = Demanddata['Supplier']
                
                if(Supplier == ''):
                    query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate],Customer_id=Customer)
                else:
                    query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier)
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    Demand_serializer = DemandSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    DemandListData = list()
                    for a in Demand_serializer:
                        DemandListData.append({
                            "id": a['id'],
                            "DemandDate": a['DemandDate'],
                            "FullDemandNumber": a['FullDemandNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "SupplierID": a['Supplier']['id'],
                            "Supplier": a['Supplier']['Name'],
                            "DemandAmount": a['DemandAmount'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DemandListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DemandView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Demanddata = JSONParser().parse(request)
                Division = Demanddata['Division']
                Customer = Demanddata['Customer']
                DemandDate = Demanddata['DemandDate']

                '''Get Max Demand Number'''
                a = GetMaxNumber.GetDemandNumber(Division, Customer, DemandDate)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                for aa in Demanddata['DemandItem']:
                    BaseUnitQuantity=UnitwiseQuantityConversion(aa['Item'],aa['Quantity'],aa['Unit'],0,0,0).GetBaseUnitQuantity()
                    Demanddata['BaseUnitQuantity'] =  BaseUnitQuantity 
                
                Demanddata['DemandNo'] = a
                '''Get Demand Prifix '''
                b = GetPrifix.GetDemandPrifix(Division)
                Demanddata['FullDemandNumber'] = b+""+str(a)
               
                Demand_serializer = DemandSerializer(data=Demanddata)
                if Demand_serializer.is_valid():
                    Demand_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Demand Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Demand_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DemandViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                OrderQuery = T_Demands.objects.filter(id=id)
                if OrderQuery.exists():
                    OrderSerializedata = DemandSerializerThird(
                        OrderQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata})
                    DemandData = list()
                    for a in OrderSerializedata:
                        DemandItemDetails = list()
                        for b in a['DemandItem']:
                            
                            DemandItemDetails.append({
                                "id": b['id'],
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRP']['MRP'],
                                "Rate": b['Rate'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GST']['GSTPercentage'],
                                "HSNCode": b['GST']['HSNCode'],
                                "Margin": b['Margin']['id'],
                                "MarginValue": b['Margin']['Margin'],
                                "BasicAmount": b['BasicAmount'],
                                "GSTAmount": b['GSTAmount'],
                                "CGST": b['CGST'],
                                "SGST": b['SGST'],
                                "IGST": b['IGST'],
                                "CGSTPercentage": b['CGSTPercentage'],
                                "SGSTPercentage": b['SGSTPercentage'],
                                "IGSTPercentage": b['IGSTPercentage'],
                                "Amount": b['Amount'],
                                "Comment": b['Comment'],
                            })
                            
                        DemandReferencesList = list()
                        for c in a['DemandReferences']:
                            DemandReferencesList.append({
                                "MaterialIssue": c['MaterialIssue'] 
                            })    
                            
                        DemandData.append({
                            "id": a['id'],
                            "DemandDate": a['DemandDate'],
                            "DemandAmount": a['DemandAmount'],
                            "FullDemandNumber": a['FullDemandNumber'],
                            "Description": a['Description'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "Supplier": a['Supplier']['id'],
                            "SupplierName": a['Supplier']['Name'],
                            "BillingAddressID": a['BillingAddress']['id'],
                            "BillingAddress": a['BillingAddress']['Address'],
                            "ShippingAddressID": a['ShippingAddress']['id'],
                            "ShippingAddress": a['ShippingAddress']['Address'],
                            "DemandItem": DemandItemDetails,
                            "DemandReferences": DemandReferencesList
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': DemandData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Demand Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
    
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Demandupdatedata = JSONParser().parse(request)
                DemandupdateByID = T_Demands.objects.get(id=id)
                Demandupdate_Serializer = DemandSerializer(
                    DemandupdateByID, data=Demandupdatedata)
                if Demandupdate_Serializer.is_valid():
                    Demandupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Demand Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Demandupdate_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Demand_Data = T_Demands.objects.get(id=id)
                Demand_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Demand Deleted Successfully', 'Data': []})
        except T_Demands.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
