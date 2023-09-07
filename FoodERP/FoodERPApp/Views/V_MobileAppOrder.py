import base64
from http.client import responses
from urllib import response
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Views.V_CommFunction import *
from ..Serializer.S_Orders import *
from ..models import *
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication

class T_MobileAppOrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                print(auth_header)
                if auth_header:
                    print('000000000')
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        print('000011111')
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    print(username,password)    
                    print('1111!1')    
                    user = authenticate(request, username=username, password=password)
                    print(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        print('aaaaaaaaaaaa')
                        Supplier = data['FoodERPSupplierID']
                        Customer = data['FoodERPRetailerID']
                        OrderDate = data['OrderDate']
                        OrderAmount = data['TotalOrderValue']
                        AppOrderNumber = data['AppOrderNumber']
                        Orderdata = list()

                        Orderitem=list()
                        
                        for aa in data['OrderItem']:
                            print(aa['FoodERPItemID'])
                            unit=MC_ItemUnits.objects.filter(UnitID_id=1,Item_id=aa['FoodERPItemID'],IsDeleted=0).values('id')
                            Gst = GSTHsnCodeMaster(aa['FoodERPItemID'], OrderDate).GetTodaysGstHsnCode()
                            BasicAmount=round(float(aa['RatewithoutGST'])*float(aa['QuantityinPieces']),2)
                            CGST= round(BasicAmount*(float(Gst[0]['GST'])/100),2)
                            BaseUnitQuantity = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 0, 0).GetBaseUnitQuantity()
                            QtyInNo = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 1, 0).ConvertintoSelectedUnit()
                            QtyInKg = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 2, 0).ConvertintoSelectedUnit()
                            QtyInBox = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 4, 0).ConvertintoSelectedUnit()
                        
                            
                            
                            Orderitem.append(
                                {
                                    "Item": aa['FoodERPItemID'],
                                    "Quantity": aa['QuantityinPieces'],
                                    "MRP": '',
                                    "MRPValue": aa['MRP'],
                                    "Rate": aa['RatewithoutGST'],
                                    "Unit": unit[0]['id'],
                                    "BaseUnitQuantity": BaseUnitQuantity,
                                    "Margin": "",
                                    "GST": Gst[0]['Gstid'],
                                    "CGST": CGST,
                                    "SGST": CGST,
                                    "IGST": 0,
                                    "GSTPercentage": float(Gst[0]['GST']),
                                    "CGSTPercentage": float(Gst[0]['GST'])/2,
                                    "SGSTPercentage": float(Gst[0]['GST'])/2,
                                    "IGSTPercentage": "0.00",
                                    "BasicAmount": BasicAmount,
                                    "GSTAmount": round(CGST+CGST,2),
                                    "Amount": round(BasicAmount+CGST+CGST,2),
                                    "TaxType": "GST",
                                    "DiscountType": "2",
                                    "Discount": 0,
                                    "DiscountAmount": "0.00",
                                    "IsDeleted": 0,
                                    "Comment": '',
                                    "QtyInNo" : QtyInNo,
                                    "QtyInKg" : QtyInKg,
                                    "QtyInBox" : QtyInBox


                                    }
                            )
                            
                        '''Get Max Order Number'''
                        a = GetMaxNumber.GetOrderNumber(Supplier, 2, OrderDate)
                        '''Get Order Prifix '''
                        b = GetPrifix.GetOrderPrifix(Supplier)
                        
                        c=MC_PartyAddress.objects.filter(Party_id=Customer,IsDefault=1).values('id')
                        print(c)
                            
                        
                        Orderdata.append({
                            
                            "OrderDate": OrderDate,
                            "DeliveryDate": OrderDate,
                            "OrderAmount": OrderAmount,
                            "Description": "",
                            "BillingAddress": c[0]['id'],
                            "ShippingAddress": c[0]['id'],
                            "OrderNo": a,
                            # "FullOrderNumber": b+""+str(a),
                            "FullOrderNumber" : AppOrderNumber,
                            "Division": Supplier,
                            "POType": 1,
                            "POFromDate": OrderDate,
                            "POToDate": OrderDate,
                            "CreatedBy": 1,
                            "UpdatedBy": 1,
                            "OrderTermsAndConditions": [
                                {
                                "TermsAndCondition": 1,
                                "IsDeleted": 0
                                }
                            ],
                            "Customer": Customer,
                            "Supplier": Supplier,
                            "OrderType": 2,
                            "IsConfirm": True,
                            "OrderItem" :  Orderitem

                        })

                        # return JsonResponse({ 'Data': Orderdata })
                        Order_serializer = T_OrderSerializer(data=Orderdata[0])
                        if Order_serializer.is_valid():
                            Order_serializer.save()
                            OrderID = Order_serializer.data['id']
                            PartyID = Order_serializer.data['Customer']
                            

                            log_entry = create_transaction_log(request, Orderdata, 0, Supplier, 'MobileAppOrder Save Successfully',1,OrderID)    
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully', 'FoodERPOrderID': OrderID})
                        log_entry = create_transaction_log(request, Orderdata, 0, 0, Order_serializer.errors,34,0)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
                    else:
                        print('bbbbbbbbbb')
                        # Invalid authorization header or authentication failed
                        return response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # log_entry = create_transaction_log(request, Orderdata, 0, 0, Exception(e),33,0)
            print('ccccccccccccccccccc')
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})



class T_MobileAppOrdersDeleteView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                print(auth_header)
                if auth_header:
                    print('000000000')
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        print('000011111')
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    print(username,password)    
                    print('1111!1')    
                    user = authenticate(request, username=username, password=password)
                    print(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        id = data['FoodERPOrderID']
                        Order_Data = T_Orders.objects.get(id=id)
                        Order_Data.delete()
                        log_entry = create_transaction_logNew(request, {'OrderID':id}, 0, 'Order Deleted Successfully',3,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully'})
        except T_Orders.DoesNotExist:
            log_entry = create_transaction_logNew(request, {'OrderID':id}, 0, 'Record Not available',29,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, {'OrderID':id}, 0, 'This Order is used in another Transaction ',8,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Order is used in another Transaction'})
        except Exception as e:
            log_entry = create_transaction_logNew(request, {'OrderID':id}, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})