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
from ..Serializer.S_MobileAppOrder import *
from ..models import *
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
import json ,requests
 
class T_MobileAppOrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
 
    @transaction.atomic()
    def post(self, request):
        data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic': 
                       
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        
                    user = authenticate(request, username=username, password=password)
                    # CustomPrint(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        # CustomPrint('aaaaaaaaaaaa')
                        Supplier = data['FoodERPSupplierID']
                        Customer = data['FoodERPRetailerID']
                        OrderDate = data['OrderDate']
                        OrderAmount = data['TotalOrderValue']
                        AppOrderNumber = data['AppOrderNumber']
                        Orderdata = list()
                        Orderitem=list()
                        

                        checkduplicate=T_Orders.objects.filter(FullOrderNumber=AppOrderNumber,Supplier_id=Supplier,OrderDate=OrderDate)
                        ordercount=checkduplicate.count()
                        if ordercount > 0:
                            log_entry = create_transaction_logNew(request, data, Supplier, 'A similar order already exists in the system, AppOrderNumber : '+data['AppOrderNumber'],161,0,0,0,Customer)
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'A similar order already exists in the system, AppOrderNumber : '+data['AppOrderNumber']})
                        else:

                            # log_entry = create_transaction_logNew(request, data, Supplier, '',149,0,0,0,Customer)

                            for aa in data['OrderItem']:
                                # Check Item Is Exist
                                ItemCheck = M_Items.objects.filter(id=aa['FoodERPItemID']).exists()
                                if not ItemCheck:
                                    log_entry = create_transaction_logNew(request, data, Supplier, f'ItemID {aa["FoodERPItemID"]} is not present in the FoodERP 2.0', 161, 0, 0, 0, Customer)
                                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': f'ItemID {aa["FoodERPItemID"]} is not present in the FoodERP 2.0'})
                                # CustomPrint(aa['FoodERPItemID'])
                                
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
                            # CustomPrint(c)
                                
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
                                "MobileAppOrderFlag" : 1,
                                "OrderTermsAndConditions": [
                                    {
                                    "TermsAndCondition": 1,
                                    "IsDeleted": 0
                                    }
                                ],
                                "AdvanceAmount" : 0,
                                "Customer": Customer,
                                "Supplier": Supplier,
                                "OrderType": 2,
                                "IsConfirm": True,
                                "OrderItem" :  Orderitem
                            }) 
                            # return JsonResponse({ 'Data': Orderdata })
                            Order_serializer = T_OrderSerializer(data=Orderdata[0])
                            # print(Order_serializer)
                            if Order_serializer.is_valid():
                                
                                Order_serializer.save()
                                
                                OrderID = Order_serializer.data['id']
                                PartyID = Order_serializer.data['Customer']
                                
                                log_entry = create_transaction_logNew(request, str(data)+','+str(Orderdata[0]), Supplier, 'MobileAppOrder Save Successfully',149,OrderID,0,0,Customer)
                                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully', 'FoodERPOrderID': OrderID})
                            log_entry = create_transaction_logNew(request, data, Supplier,  Order_serializer.errors,161,OrderID,0,0,Customer)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
                    else:
                        # CustomPrint('bbbbbbbbbb')
                        log_entry = create_transaction_logNew(request, data, 0,  'Unauthorized',161,0,0,0,0)
                        # Invalid authorization header or authentication failed
                        return response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0,'MobileAppOrderSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


    @transaction.atomic()
    def put(self, request,id=0):
        data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                # CustomPrint(auth_header)
                if auth_header:
                    # CustomPrint('000000000')
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # CustomPrint('000011111')
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    # CustomPrint(username,password)    
                    # CustomPrint('1111!1')    
                    user = authenticate(request, username=username, password=password)
                    # CustomPrint(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        # CustomPrint('aaaaaaaaaaaa')
                        # CustomPrint(id)
                        OrderupdateByID = T_Orders.objects.get(id=id)
                        # CustomPrint(OrderupdateByID)
                        Supplier = data['FoodERPSupplierID']
                        Customer = data['FoodERPRetailerID']
                        OrderDate = data['OrderDate']
                        OrderAmount = data['TotalOrderValue']
                        AppOrderNumber = data['AppOrderNumber']
                        Orderdata = list()

                        Orderitem=list()
                        
                        for aa in data['OrderItem']:
                            # CustomPrint(aa['FoodERPItemID'])
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
                                    "IsDeleted": 1,
                                    "Comment": '',
                                    "QtyInNo" : QtyInNo,
                                    "QtyInKg" : QtyInKg,
                                    "QtyInBox" : QtyInBox


                                    }
                            )
                            
                        '''Get Max Order Number'''
                        a = GetMaxNumber.GetOrderNumber(Supplier, 2, OrderDate)
                        '''Get Order Prifix '''
                        # b = GetPrifix.GetOrderPrifix(Supplier)
                        
                        c=MC_PartyAddress.objects.filter(Party_id=Customer,IsDefault=1).values('id')
                         
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
                        Order_serializer = T_OrderSerializerMobileapp(
                    OrderupdateByID, data=Orderdata[0])
                        # Order_serializer = T_OrderSerializer(data=Orderdata[0])
                        if Order_serializer.is_valid():
                            Order_serializer.save()
                            OrderID = Order_serializer.data['id']
                            Customer = Order_serializer.data['Customer']
                            
                            log_entry = create_transaction_logNew(request, data, Supplier, 'MobileAppOrder Update Successfully',150,OrderID,0,0,Customer)
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Update Successfully', 'FoodERPOrderID': OrderID})
                        log_entry = create_transaction_logNew(request, data, Supplier, Order_serializer.errors,162,OrderID,0,0,Customer)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
                    else:
                        # Invalid authorization header or authentication failed
                        return response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0,  str(e),162,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class T_MobileAppOrdersDeleteView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request, id=0):
        data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                # CustomPrint(auth_header)
                if auth_header:
                    # CustomPrint('000000000')
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # CustomPrint('000011111')
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    # CustomPrint(username,password)    
                    # CustomPrint('1111!1')    
                    user = authenticate(request, username=username, password=password)
                    # CustomPrint(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        id = data['FoodERPOrderID']
                        Order_Data = T_Orders.objects.get(id=id)
                        Order_Data.delete()
                        log_entry = create_transaction_logNew(request, {'OrderID':id}, 0,'MobileAPPOrder Deleted Successfully',151,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully'})
        except T_Orders.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0, 0,'MobileAPPOrder Not available',163,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'This Order is used in another Transaction ',163,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Order is used in another Transaction'})
        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0,str(e),163,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class NewProductSendToMobileAppView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
 
   
    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                
                ItemData=list()
                today = date.today()
                q0=M_Items.objects.raw('''SELECT M_Items.id ,M_Items.Name ItemName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') FoodERPParentName,ifnull(MC_SubGroup.Name,'') FoodERPFamilyName 
,ifnull(MC_ItemGroupDetails.GroupType_id,'') GroupTypeId,ifnull(MC_ItemGroupDetails.Group_id,'') FoodERPParentId,ifnull(MC_ItemGroupDetails.SubGroup_id,0) FoodERPFamilyId,M_Items.BaseUnitID_id,M_Items.isActive
,GSTHsnCodeMaster(M_Items.id,%s,3,0,0) HSNCode,GetTodaysDateMRP(M_Items.id,%s,2,0,0,0) MRPValue
FROM M_Items
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
where M_Items.id=%s''',([today],[today],[id]))
    
                for row in q0:
                     
                    RetaileRate=RateCalculationFunction(0,row.id,0,0,1,0,3).RateWithGST() 
                    DistributorRate=RateCalculationFunction(0,row.id,0,0,1,0,2).RateWithGST()
                    SuperStockistRate=RateCalculationFunction(0,row.id,0,0,1,0,1).RateWithGST()
                    if row.isActive == True:
                        ss='true'
                    else:
                        ss='false'    
                    ItemData.append({
                            "FoodERPItemID": str(row.id),
                            "FoodERPCategoryId":1,
                            "FoodERPFamilyId":int(row.FoodERPFamilyId),
                            "FoodERPTypeId":1,
                            "FoodERPUomId":row.BaseUnitID_id,
                            "ItemName":row.ItemName,
                            "MRP":float(row.MRPValue),
                            "RetailerRate":float(RetaileRate[0]['RateWithoutGST']),
                            "DistributorRate":float(DistributorRate[0]['RateWithoutGST']),
                            "SuperStockistRate":float(SuperStockistRate[0]['RateWithoutGST']),
                            "ProductHSN":row.HSNCode,
                            "IsActive":bool(ss)
                            
                        })

                payload={
                    "products" : ItemData
                }

                # url = "http://webapp.theskygge.com/fmcg_middleware/products/add"
                # 'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7',
                SkyggeURL, Token  = GetThirdPartyAPIs(18)
                url = SkyggeURL
                
                headers = {
                            'SecureToken': Token,
                            'Content-Type': 'application/json'
                          }
                
                
                payload_json_data = json.dumps(payload)
                
                response = requests.request("POST", url, headers=headers, data=payload_json_data)
                
                response_json=json.loads(response.text)
                
                # CustomPrint('==============================',response_json['success'])
                if(response_json['success'] == True):
                    log_entry = create_transaction_logNew(request, payload_json_data, 0,response_json,152,0)
                    for a in response_json['data']:
                        query = M_Items.objects.filter(id=id).update(SkyggeProductID =a['productId'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': payload_json_data})
                else:
                    log_entry = create_transaction_logNew(request, payload_json_data, 0,response_json['message'],164,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':response_json, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,response_json,164,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})            
        
    @transaction.atomic()
    def put(self, request,id=0):
        Productdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ProductID = Productdata['products']
                ProductID_list = ProductID.split(",")
                # CustomPrint(ProductID_list)
                ItemData=list()
                today = date.today()
                q0=M_Items.objects.raw('''SELECT M_Items.id ,M_Items.Name ItemName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') FoodERPParentName,ifnull(MC_SubGroup.Name,'') FoodERPFamilyName 
,ifnull(MC_ItemGroupDetails.GroupType_id,'') GroupTypeId,ifnull(MC_ItemGroupDetails.Group_id,'') FoodERPParentId,ifnull(MC_ItemGroupDetails.SubGroup_id,'') FoodERPFamilyId,M_Items.BaseUnitID_id,M_Items.isActive
,GSTHsnCodeMaster(M_Items.id,%s,3,0,0) HSNCode,GetTodaysDateMRP(M_Items.id,%s,2,0,0,0) MRPValue
FROM M_Items
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
where M_Items.id in %s''',([today],[today],ProductID_list))
                # CustomPrint(q0)
                for row in q0:
                    RetaileRate=RateCalculationFunction(0,row.id,0,0,1,0,3).RateWithGST() 
                    DistributorRate=RateCalculationFunction(0,row.id,0,0,1,0,2).RateWithGST()
                    SuperStockistRate=RateCalculationFunction(0,row.id,0,0,1,0,1).RateWithGST() 
                    # ItemData.append({
                    #         "FoodERPItemID": str(row.id),
                    #         "FoodERPCategoryId":1,
                    #         "FoodERPFamilyId":row.FoodERPFamilyId,
                    #         "FoodERPTypeId":1,
                    #         "FoodERPUomId":row.BaseUnitID_id,
                    #         "ItemName":row.ItemName,
                    #         "MRP":float(row.MRPValue),
                    #         "RetailerRate":float(RetaileRate[0]['RateWithoutGST']),
                    #         "DistributorRate":float(DistributorRate[0]['RateWithoutGST']),
                    #         "SuperStockistRate":float(SuperStockistRate[0]['RateWithoutGST']),
                    #         "ProductHSN":row.HSNCode,
                    #         "IsActive":row.isActive
                            
                    #     })

                payload={
                    "products" : ItemData
                }
                # url = "http://webapp.theskygge.com/fmcg_middleware/products/update"
                SkyggeURL, Token  = GetThirdPartyAPIs(19)
                url = SkyggeURL
                headers = {
                            'SecureToken': Token,
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                # print('mobileappdat: -',payload_json_data)
                response = requests.request("put", url, headers=headers, data=payload_json_data)
                response_json=json.loads(response.text)
                
                if(response_json['success'] == True):
                    log_entry = create_transaction_logNew(request, Productdata, 0,response_json['message'],153,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})
                else:
                    # CustomPrint('aaaaaaaaaaaaaaaaa')
                    log_entry = create_transaction_logNew(request, Productdata, 0,response_json['message'],165,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request,Productdata, 0,'ProductSendToMobileAppUpdate:'+str(e),165,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})                
        
    @transaction.atomic()
    def delete(self, request,id=0):
        try:
            with transaction.atomic():
                payload = json.dumps({
                "products": [
                    {
                    "FoodERPItemID": id
                    }
                ]
                })
                
                # url = "http://webapp.theskygge.com/fmcg_middleware/products/delete"
                # 'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7'
               
                SkyggeURL, Token  = GetThirdPartyAPIs(20)
                url = SkyggeURL
               
                headers = {
                'SecureToken': Token,
                'Content-Type': 'application/json'
                }

                response = requests.request("DELETE", url, headers=headers, data=payload)
                response_json=json.loads(response.text)
                if(response_json['success'] == True):
                    log_entry = create_transaction_logNew(request, payload, 0, 0,response_json,154,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, payload, 0, 0,response_json,166,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})     
            
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'ProductSendToMobileAppDelete:'+str(e),166,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})    
        
class NewRetailerSendToMobileAppView(CreateAPIView):
    permission_classes = (IsAuthenticated,)        

    @transaction.atomic()
    def post(self, request,id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                RetailerID = Orderdata['RetailerID']
                DistributorID= Orderdata['DistributorID']
                RetailerID_list = RetailerID.split(",")
                # CustomPrint(RetailerID_list)
                RetailerData=list()
                today = date.today()
                q0=M_Parties.objects.raw('''SELECT cust.id,cust.Name RetailerName,(cust.MobileNo) MobileNumber,cust.Email EmailAddress,cust.PAN PANNumber,
cust.GSTIN GSTNumber,cust.Latitude, cust.Longitude,dist.id distid,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,
(select Route_id from MC_PartySubParty where Party_id=dist.id and SubParty_id=cust.id )Route_id,MC_PartyAddress.Address
 FROM MC_PartySubParty 
 join M_Parties dist on dist.id=MC_PartySubParty.Party_id
 join M_Parties cust on cust.id=MC_PartySubParty.SubParty_id
 left join MC_PartyAddress on cust.id = MC_PartyAddress.Party_id and MC_PartyAddress.IsDefault=0
 where MC_PartySubParty.Party_id= %s and  cust.PartyType_id=11 and cust.id in %s''',(DistributorID,RetailerID_list))
                # CustomPrint(q0.query)
                for row in q0:
                    # CustomPrint(row) 
                    RetailerData.append({
                            "FoodERPRetailerID": str(row.id),
                            # "RouteId"       :row.Route_id,
                            "RouteId" : 1,
                            "RetailerName"  :row.RetailerName,
                            "DistributorID" :row.distid,
                            "Address"       :row.Address,
                            "MobileNumber"  :str(row.MobileNumber),
                            "EmailAddress"  :row.EmailAddress,
                            "PANNumber"     :row.PANNumber,
                            "GSTNumber"     :row.GSTNumber,
                            "FSSAINumber"   :row.FSSAINo,
                            "FSSAIExpiry"   :row.FSSAIExipry,
                            # "Latitude"      :row.Latitude,
                            # "Longitude"     :row.Longitude,
                            "IsActive"      :row.isActive
                           
                            
                        })

                payload={
                    "outlets" : RetailerData
                }
                # CustomPrint(payload)
                # url = "http://webapp.theskygge.com/fmcg_middleware/outlets/add"
                SkyggeURL, Token  = GetThirdPartyAPIs(21)
                url = SkyggeURL
                # CustomPrint(url)
                headers = {
                            'SecureToken': Token,
                            'Content-Type': 'application/json'
                          }
                # CustomPrint('8(((((888(((((((8((((((((8(((((((((((((((((((((8',payload)
                payload_json_data = json.dumps(payload)
                
                # CustomPrint(payload_json_data)
                response = requests.request(
                    "POST", url, headers=headers, data=payload_json_data)
             
                response_json=json.loads(response.text)
                # CustomPrint(response_json)
                if(response_json['success'] == True):
                    log_entry = create_transaction_logNew(request,Orderdata,0,response_json['message'],155,0)
                    for a in response_json['data']:
                        query = M_Parties.objects.filter(id=a['externalMappingId']).update(SkyggeID =a['outletId'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,Orderdata,0,response_json['message'],167,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':response_json['message'], 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Orderdata,0,'RetailerSendToMobileAppSave:'+str(e),167,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})            
        
    @transaction.atomic()
    def put(self, request,id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                RetailerID = Orderdata['RetailerID']
                DistributorID= Orderdata['DistributorID']
                RetailerID_list = RetailerID.split(",")
                RetailerData=list()
                today = date.today()
                q0=M_Parties.objects.raw('''SELECT cust.id,cust.Name RetailerName,cust.MobileNo MobileNumber,cust.Email EmailAddress,cust.PAN PANNumber,
cust.GSTIN GSTNumber,cust.Latitude,cust.Longitude,dist.id distid,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,
(select Route_id from MC_PartySubParty where Party_id=dist.id and SubParty_id=cust.id )Route_id,MC_PartyAddress.Address
 FROM MC_PartySubParty 
 join M_Parties dist on dist.id=MC_PartySubParty.Party_id
 join M_Parties cust on cust.id=MC_PartySubParty.SubParty_id
 left join MC_PartyAddress on cust.id = MC_PartyAddress.Party_id and MC_PartyAddress.IsDefault=0
 where MC_PartySubParty.Party_id= %s and cust.PartyType_id=11 and cust.id in %s''',(DistributorID,RetailerID_list))
                # CustomPrint(q0.query)
                for row in q0:
                    # CustomPrint(row.isActive)
                    RetailerData.append({
                            "FoodERPRetailerID": str(row.id),
                            # "RouteId"       :row.Route_id,
                            "RouteId" : 1,
                            "RetailerName"  :row.RetailerName,
                            "DistributorID" :row.distid,
                            "Address"       :row.Address,
                            "MobileNumber"  :str(row.MobileNumber),
                            "EmailAddress"  :row.EmailAddress,
                            "PANNumber"     :row.PANNumber,
                            "GSTNumber"     :row.GSTNumber,
                            "FSSAINumber"   :row.FSSAINo,
                            "FSSAIExpiry"   :row.FSSAIExipry,
                            # "Latitude"      :row.Latitude,
                            # "Longitude"     :row.Longitude,
                            "IsActive"      :row.isActive
                           
                            
                        })
                # CustomPrint('333333333',RetailerData)
                payload={
                    "outlets" : RetailerData
                }
                # url = "http://webapp.theskygge.com/fmcg_middleware/outlets/update"
                SkyggeURL, Token  = GetThirdPartyAPIs(22)
                url = SkyggeURL
                headers = {
                            'SecureToken': Token,
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                # CustomPrint(payload_json_data)
                response = requests.request("put", url, headers=headers, data=payload_json_data)
                response_json=json.loads(response.text)
                # CustomPrint('======================',response_json)
                if(response_json['success'] == True):
                    log_entry = create_transaction_logNew(request, Orderdata, 0,response_json['message'],156,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, Orderdata, 0,response_json['message'],168,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':response_json['message'], 'Data': []})    
            
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0,'RetailerSendToMobileAppUpdate:'+str(e),168,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})            
            
    @transaction.atomic()
    def delete(self, request,id=0):
        try:
            with transaction.atomic():
                
                RetailerData=list()
                
                RetailerData.append({
                        
                        "FoodERPRetailerID" : id 
                    })

                payload={
                    "outlets" : RetailerData
                }
                # url = "http://webapp.theskygge.com/fmcg_middleware/outlets/delete"
                SkyggeURL, Token  = GetThirdPartyAPIs(23)
                url = SkyggeURL
                headers = {
                            'SecureToken': Token,
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                response = requests.request("delete", url, headers=headers, data=payload_json_data)
                # CustomPrint(response.text)
                response_json=json.loads(response.text)
                
                if(response_json['success'] == True):
                    log_entry = create_transaction_logNew(request, payload, 0,response_json['message'],157)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, payload, 0,response_json['message'],169)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':response_json['message'], 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'RetailerSendToMobileAppDelete:'+str(e),169,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})  
        
        
        
class RetailerAddFromMobileAppview(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    
                    user = authenticate(request, username=username, password=password)
                    
                    RetailerAddList=list()
                    for a in data['outlets']:
                        query1 = M_Parties.objects.filter(id=a['DistributorId']).values('State_id','District_id','City_id')
                        if query1:

                            PartySubParty = list()
                            PartySubParty.append({
                                "Party":a['DistributorId'],
                                "Route": "",
                                "CreatedBy":430,
                                "UpdatedBy":430,  
                            })
                            PartyAddress = list()
                            PartyAddress.append({
                                "Address": a['Address'],
                                "FSSAINo": a['FSSAINumber'],
                                "FSSAIExipry": a['FSSAIExpiry'],
                                "IsDefault": True, 
                            })
                            PartyPrefix = list()
                            PartyPrefix.append({
                                "Orderprefix": "PO",
                                "Invoiceprefix": "IN",
                                "Grnprefix": "GRN",
                                "Receiptprefix": "RE",
                                "WorkOrderprefix": "",
                                "MaterialIssueprefix": "",
                                "Demandprefix": "",
                                "IBChallanprefix": "",
                                "IBInwardprefix": "",
                                "PurchaseReturnprefix": "PR",
                                "Creditprefix": "CR",
                                "Debitprefix": "DR" 
                            })
                            
                            RetailerAddList.append(
                                {
                                    "Name":a['RetailerName'],
                                    "PriceList": 3,
                                    "PartyType": 11,
                                    "Company": 3,
                                    "PAN": a['PANNumber'],
                                    "Email":a['EmailAddress'],
                                    "MobileNo": a['MobileNumber'],
                                    "Latitude": a['Latitude'],
                                    "Longitude": a['Longitude'],
                                    "GSTIN": a['GSTNumber'],
                                    "isActive": a['IsActive'],
                                    "CreatedBy":430,
                                    "UpdatedBy":430,
                                    "IsApprovedParty":1,
                                    "State":query1[0]['State_id'], #Compensary
                                    "District":query1[0]['District_id'], #Compensary
                                    "City":query1[0]['City_id'], #Compensary
                                    "PartySubParty":PartySubParty,
                                    "PartyAddress":PartyAddress,
                                    "PartyPrefix":PartyPrefix
                                })
                        else:
                            log_entry = create_transaction_logNew(request, data, 0,'Invalid DistributorId',170,0)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'Invalid DistributorId'})

                    inserted_retailerlist = list()     
                    for aa in RetailerAddList:
                        Retailer_serializer = RetailerAddFromMobileAppSerializer(data=aa)
                        if Retailer_serializer.is_valid():
                            Retailer = Retailer_serializer.save()
                            inserted_retailerlist.append({
                                "FoodERPRetailerID":Retailer.id,
                                "RetailerName":Retailer.Name,
                                "GSTNumber":Retailer.GSTIN
                            })
                        else:
                            log_entry = create_transaction_logNew(request, data, 0,'fail to Added Retailer From MobileApp ',170,0)
                            transaction.set_rollback(True)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Retailer_serializer.errors})
                    log_entry = create_transaction_logNew(request,data,0,'Retailer Added From MobileApp Successfully',158,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Added From App Successfully','InsertedoutletsCount': len(inserted_retailerlist),"outlets":inserted_retailerlist})                        
        except Exception as e:
            log_entry = create_transaction_logNew(request,data,0,'RetailerAddedFromMobileApp:'+str(e),170,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e) })
        
        
        
class RetailerUpdateFromMobileAppview(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    
                    user = authenticate(request, username=username, password=password)
                    
                    RetailerAddList=list()
                    for a in data['outlets']:
                        
                        PartyAddress = list()
                        PartyAddress.append({
                            "FoodERPRetailerID":a['FoodERPRetailerID'],
                            "Address": a['Address'],
                            "FSSAINo": a['FSSAINumber'],
                            "FSSAIExipry": a['FSSAIExpiry']
                           
                        })
                        RetailerAddList.append(
                            {
                                "FoodERPRetailerID":a['FoodERPRetailerID'],
                                "Name":a['RetailerName'],
                                "PAN": a['PANNumber'],
                                "Email":a['EmailAddress'],
                                "MobileNo": a['MobileNumber'],
                                "Latitude": a['Latitude'],
                                "Longitude": a['Longitude'],
                                "GSTIN": a['GSTNumber'],
                                "isActive": a['IsActive'],
                                "UpdatedBy":430,
                                "PartyAddress":PartyAddress
                            })
                    
                    # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message':RetailerAddList, 'Data': []})    
                    for aa in RetailerAddList:
                        PartiesdataByID = M_Parties.objects.get(id=aa['FoodERPRetailerID'])
                        Retailer_serializer = RetailerUpdateFromMobileAppSerializer(PartiesdataByID, data=aa)
                        if Retailer_serializer.is_valid():
                            Retailer = Retailer_serializer.save()
                            # log_entry = create_transaction_logNew(request, data, 0,'Retailer Updated From Mobile App Successfully',159,0)
                            # return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Updated From Mobile App Successfully' })
                        else:
                            log_entry = create_transaction_logNew(request, data, 0,'RetailerUpdatedFromMobileApp:'+str(Retailer_serializer.errors),171,0)
                            transaction.set_rollback(True)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Retailer_serializer.errors})
                    log_entry = create_transaction_logNew(request, data, 0,'Retailer Updated From Mobile App Successfully',159,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Updated From Mobile App Successfully' })                        
        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0,'RetailerUpdatedFromMobileApp:'+str(e),171,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []}) 

class RetailerDeleteFromMobileApp(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
                  
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    user = authenticate(request, username=username, password=password)
                    M_Partiesdata = M_Parties.objects.get(id=id)
                    M_Partiesdata.delete()
                    log_entry = create_transaction_logNew(request,{'RetailerID':id}, 0,'Deleted Successfully',160,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Retailer Deleted Successfully'})
        except M_Parties.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0, 0,'Retailer Not available',172,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Retailer Not available'})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0, 0,'Retailer used in another table',172,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Retailer used in another table'})              
                 