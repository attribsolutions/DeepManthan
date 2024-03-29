from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Views.V_CommFunction import *
from ..Serializer.S_Orders import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *
from ..Serializer.S_Bom import *
from ..Serializer.S_Challan import *
from ..Serializer.S_Invoices import *
from django.db.models import Sum
from ..models import *


class POTypeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PoTypedata = M_POType.objects.all()
                if PoTypedata.exists():
                    PoTypedata_serializer = M_POTypeserializer(
                        PoTypedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PoTypedata_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'POType Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class OrderListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Supplier = Orderdata['Supplier']
                OrderType = Orderdata['OrderType']
                CustomerType = Orderdata['CustomerType']
                d = date.today()   

                # for log
                if OrderType == 1:
                    x = Customer
                    if Supplier == '':
                        z = 0
                        log_entry = create_transaction_logNew(request, Orderdata,x,'From:'+FromDate+','+'To:'+ToDate,28,0,FromDate,ToDate,0)
                    else:
                        z = Supplier
                        log_entry = create_transaction_logNew(request, Orderdata,z,'From:'+FromDate+','+'To:'+ToDate+','+'Supplier:'+str(z),28,0,FromDate,ToDate,x)
                else:
                    x = Supplier
                    if Customer == '':
                        z = 0
                        log_entry = create_transaction_logNew(request, Orderdata,x,'From:'+FromDate+','+'To:'+ToDate+','+'Supplier:'+str(x),173,0,FromDate,ToDate,0)
                    else:
                        z = Customer
                        log_entry = create_transaction_logNew(request, Orderdata,x,'From:'+FromDate+','+'To:'+ToDate+','+'Supplier:'+str(x),173,0,FromDate,ToDate,z)

                if(OrderType == 1):  # OrderType -1 PO Order
                    if(Supplier == ''):

                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Customer_id=Customer, OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate=FromDate, POToDate=ToDate, Customer_id=Customer, OrderType=1)
                        q = query.union(queryForOpenPO)
                    else:
                        query = T_Orders.objects.filter(OrderDate__range=[
                                                        FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate=FromDate, POToDate=ToDate, Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        q = query.union(queryForOpenPO)
                else:  # OrderType -2 Sales Order
                    # Pradnya :  OrderType=2 filter remove form all ORM Query coz parasnath purches order is katraj div sale order
                    if(CustomerType == ''):  # all
                        aaa = Q()
                    else:
                        CustomerType_list = CustomerType.split(",")
                        aaa = Q(Customer__PriceList_id__in=CustomerType_list)

                    if(Customer == ''):

                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Supplier_id=Supplier).select_related('Customer').filter(aaa)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=FromDate, POToDate__gte=ToDate, Supplier_id=Supplier).select_related('Customer').filter(aaa)
                        q = query.union(queryForOpenPO)
                    else:

                        query = T_Orders.objects.filter(OrderDate__range=[
                                                        FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier).select_related('Customer').filter(aaa)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=FromDate, POToDate__gte=ToDate, Customer_id=Customer, Supplier_id=Supplier).select_related('Customer').filter(aaa)
                        q = query.union(queryForOpenPO)
                # print(query.query)
                # return JsonResponse({'query': str(q.query)})
                if q:
                    Order_serializer = T_OrderSerializerSecond(
                        q, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    OrderListData = list()
                    for a in Order_serializer:
                        
                        
                        if (Orderdata['DashBoardMode'] == 1):
                            OrderListData.append({
                                "OrderDate": a['OrderDate'],
                                "MobileAppOrderFlag" : a['MobileAppOrderFlag']
                            })
                        else:
                            tcsflagquery = MC_PartySubParty.objects.filter(Party=a['Supplier']['id'],SubParty=a['Customer']['id']).values('IsTCSParty')
                            if tcsflagquery:
                                TCSPartyFlag= tcsflagquery[0]['IsTCSParty']   
                            else:
                                TCSPartyFlag = False    
                                
                            inward = 0
                            for c in a['OrderReferences']:
                                if(c['Inward'] == 1):
                                    inward = 1

                            Count = TC_InvoicesReferences.objects.filter(
                                Order=a['id']).count()
                            if Count == 0:
                                InvoiceCreated = False
                            else:
                                InvoiceCreated = True
                            
                            OrderListData.append({
                                "id": a['id'],
                                "OrderDate": a['OrderDate'],
                                "FullOrderNumber": a['FullOrderNumber'],
                                "DeliveryDate": a['DeliveryDate'],
                                "CustomerID": a['Customer']['id'],
                                "Customer": a['Customer']['Name'],
                                "CustomerSAPCode": a['Customer']['SAPPartyCode'],
                                "CustomerPAN" : a['Customer']['PAN'],
                                "CustomerGSTIN":a['Customer']['GSTIN'],
                                "SupplierSAPCode": a['Supplier']['SAPPartyCode'],
                                "SupplierPAN" : a['Supplier']['PAN'],
                                "SupplierGSTIN": a['Supplier']['GSTIN'],
                                "SupplierID": a['Supplier']['id'],
                                "Supplier": a['Supplier']['Name'],
                                "OrderAmount": a['OrderAmount'],
                                "Description": a['Description'],
                                "OrderType": a['OrderType'],
                                "POType": a['POType']['Name'],
                                "BillingAddress": a['BillingAddress']['Address'],
                                "ShippingAddress": a['ShippingAddress']['Address'],
                                "InvoiceCreated": InvoiceCreated,
                                "CreatedBy": a['CreatedBy'],
                                "CreatedOn": a['CreatedOn'],
                                "SAPResponse": a['SAPResponse'],
                                "IsConfirm": a['IsConfirm'],
                                "Inward": inward,
                                "IsTCSParty":TCSPartyFlag,
                                "MobileAppOrderFlag" : a['MobileAppOrderFlag']
                            })

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': OrderListData})
                log_entry = create_transaction_logNew(request, Orderdata, x, "Order List Not Found",28,0,FromDate,ToDate,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, Orderdata, 0,'OrderList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class OrderListFilterViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Supplier = Orderdata['Supplier']
                OrderType = Orderdata['OrderType']

                d = date.today()

                #for log
                if OrderType == 3:
                    x = Customer
                    if Supplier == '':
                        z = 0
                    else:
                        z = Supplier
                else:
                    x = Supplier
                    if Customer == '':
                        z = 0
                    else:
                        z = Customer

                if(OrderType == 3):  # OrderType - 3 for GRN STP Showing Invoices for Making GRN
                    if(Supplier == ''):
                        if (FromDate == '' and ToDate == ''):
                            # query = T_Invoices.objects.filter(Customer_id=Customer).order_by('-CreatedOn')
                            query = T_Invoices.objects.raw('''select  T_Invoices.id,InvoiceDate,FullInvoiceNumber,supl.id SupplierID,supl.Name SupplierName,cust.id CustomerID,cust.Name CustomerName,GrandTotal,T_Invoices.CreatedBy,T_Invoices.CreatedOn,Hide 
,TC_GRNReferences.Invoice_id
from T_Invoices
join M_Parties supl on supl.id=T_Invoices.Party_id
join M_Parties cust on cust.id=T_Invoices.Customer_id
left join TC_GRNReferences on T_Invoices.id=TC_GRNReferences.Invoice_id 
where  Customer_id=%s and TC_GRNReferences.Invoice_id is null order by CreatedOn desc ''',[Customer])
                        else:
                            # query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate],Customer_id=Customer).order_by('-CreatedOn')
                            query = T_Invoices.objects.raw('''select  T_Invoices.id,InvoiceDate,FullInvoiceNumber,supl.id SupplierID,supl.Name SupplierName,cust.id CustomerID,cust.Name CustomerName,GrandTotal,T_Invoices.CreatedBy,T_Invoices.CreatedOn,Hide 
,TC_GRNReferences.Invoice_id
from T_Invoices
join M_Parties supl on supl.id=T_Invoices.Party_id
join M_Parties cust on cust.id=T_Invoices.Customer_id
left join TC_GRNReferences on T_Invoices.id=TC_GRNReferences.Invoice_id 
where T_Invoices.InvoiceDate between %s and %s and Customer_id=%s and TC_GRNReferences.Invoice_id is null order by CreatedOn desc ''',([FromDate],[ToDate],[Customer]))

                    else:
                        # query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Supplier).order_by('-CreatedOn')
                        query = T_Invoices.objects.raw('''select  T_Invoices.id,InvoiceDate,FullInvoiceNumber,supl.id SupplierID,supl.Name SupplierName,cust.id CustomerID,cust.Name CustomerName,GrandTotal,T_Invoices.CreatedBy,T_Invoices.CreatedOn,Hide 
,TC_GRNReferences.Invoice_id
from T_Invoices
join M_Parties supl on supl.id=T_Invoices.Party_id
join M_Parties cust on cust.id=T_Invoices.Customer_id
left join TC_GRNReferences on T_Invoices.id=TC_GRNReferences.Invoice_id 
where T_Invoices.InvoiceDate between %s and %s and  Customer_id=%s and Party_id=%s and TC_GRNReferences.Invoice_id is null order by CreatedOn desc ''',([FromDate],[ToDate],[Customer],[Supplier]))
                    # return JsonResponse({'query': str(Orderdata.query)})
                    
                   
                    if query: 
                        # Invoice_serializer = InvoiceSerializerSecond(
                        #     query, many=True).data
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                        InvoiceListData = list()
                        for a in query:

                             
                            # InvoiceID = TC_GRNReferences.objects.filter(
                            #     Invoice=a['id']).values('Invoice').count()
                            # if InvoiceID == 0:
                            InvoiceListData.append({
                                "id": a.id,
                                "OrderDate": a.InvoiceDate,
                                "FullOrderNumber": a.FullInvoiceNumber,
                                "DeliveryDate": "",
                                "CustomerID": a.CustomerID,
                                "Customer": a.CustomerName,
                                "SupplierID": a.SupplierID,
                                "Supplier": a.SupplierName,
                                "OrderAmount": a.GrandTotal,
                                "Description": "",
                                "OrderType": "",
                                "POType": "",
                                "BillingAddress": "",
                                "ShippingAddress": "",
                                "CreatedBy": a.CreatedBy,
                                "CreatedOn": a.CreatedOn,
                                "Inward": "",
                                "Percentage": "",
                                "IsRecordDeleted":a.Hide,
                            })
                        log_entry = create_transaction_logNew(request, Orderdata, z,'From:'+FromDate+','+'To:'+ToDate,28,0,FromDate,ToDate,x)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                    log_entry = create_transaction_logNew(request, Orderdata, z, "Order List Not Found",28,0,FromDate,ToDate,x)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

                elif(OrderType == 1):  # OrderType -1 PO Order
                    if(Supplier == ''):
                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Customer_id=Customer,  OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, OrderType=1)
                        q = query.union(queryForOpenPO)
                    else:
                        query = T_Orders.objects.filter(OrderDate__range=[
                                                        FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, Supplier_id=Supplier, OrderType=1)
                        q = query.union(queryForOpenPO)
                else:  # OrderType -2 Sales Order
                    if(Customer == ''):
                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Supplier_id=Supplier, OrderType=2)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=d, POToDate__gte=d, Supplier_id=Supplier, OrderType=2)
                        q = query.union(queryForOpenPO)
                    else:
                        query = T_Orders.objects.filter(OrderDate__range=[
                                                        FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier, OrderType=2)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=d, POToDate__gte=d, Customer_id=Customer, Supplier_id=Supplier, OrderType=2)
                        q = query.union(queryForOpenPO)
                # return JsonResponse({'query': str(Orderdata.query)})

                Order_serializer = T_OrderSerializerSecond(q, many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                OrderListData = list()
                for a in Order_serializer:
                    inward = 0
                    for c in a['OrderReferences']:
                        if(c['Inward'] == 1):
                            inward = 1
                    OrderListData.append({
                        "id": a['id'],
                        "OrderDate": a['OrderDate'],
                        "FullOrderNumber": a['FullOrderNumber'],
                        "DeliveryDate": a['DeliveryDate'],
                        "CustomerID": a['Customer']['id'],
                        "Customer": a['Customer']['Name'],
                        "SupplierID": a['Supplier']['id'],
                        "Supplier": a['Supplier']['Name'],
                        "OrderAmount": a['OrderAmount'],
                        "Description": a['Description'],
                        "OrderType": a['OrderType'],
                        "POType": a['POType']['Name'],
                        "BillingAddress": a['BillingAddress']['Address'],
                        "ShippingAddress": a['ShippingAddress']['Address'],
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "SAPResponse": a['SAPResponse'],
                        "Inward": inward,
                        "Percentage": "",

                    })

                Challanquery = T_Challan.objects.filter(Party=Customer)
                Challan_serializer = ChallanSerializerList(
                    Challanquery, many=True).data
                for a in Challan_serializer:
                    Query = TC_GRNReferences.objects.filter(
                        Challan_id=a['id']).select_related('GRN').values('GRN_id')
                    GRNList = list()
                    for b in Query:
                        GRNList.append(b['GRN_id'])
                        if not GRNList:
                            Percentage = 0
                        else:
                            y = tuple(GRNList)
                            Itemsquery = TC_GRNItems.objects.filter(
                                GRN__in=y).aggregate(Sum('Quantity'))
                            Percentage = (
                                float(Itemsquery['Quantity__sum'])/float(a['ChallanItems'][0]['Quantity']))*100

                    OrderListData.append({
                        "id": a['id'],
                        "OrderDate": a['ChallanDate'],
                        "DeliveryDate": "",
                        "FullOrderNumber": a['FullChallanNumber'],
                        "CustomerID": a['Customer']['id'],
                        "Customer": a['Customer']['Name'],
                        "SupplierID": a['Party']['id'],
                        "Supplier": a['Party']['Name'],
                        "OrderAmount": a['GrandTotal'],
                        "Description": "",
                        "OrderType": "",
                        "POType": "Challan",
                        "BillingAddress": "",
                        "ShippingAddress": "",
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "Inward": "",
                        "Percentage": Percentage,

                    })
                log_entry = create_transaction_logNew(request, Orderdata, z,'From:'+FromDate+','+'To:'+ToDate,28,0,FromDate,ToDate,x)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': OrderListData})
            log_entry = create_transaction_logNew(request, Orderdata, z, "Order Not available",28,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'OrderListSecond:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class T_OrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                Division = Orderdata['Division']
                OrderType = Orderdata['OrderType']
                OrderDate = Orderdata['OrderDate']
                Supplier  = Orderdata['Supplier']
                '''Get Max Order Number'''
                a = GetMaxNumber.GetOrderNumber(Supplier, OrderType, OrderDate)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                
                for aa in Orderdata['OrderItem']:

                    BaseUnitQuantity = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 0, 0).GetBaseUnitQuantity()
                    aa['BaseUnitQuantity'] = BaseUnitQuantity
                    QtyInNo = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 1, 0).ConvertintoSelectedUnit()
                    aa['QtyInNo'] = QtyInNo
                    QtyInKg = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 2, 0).ConvertintoSelectedUnit()
                    aa['QtyInKg'] = QtyInKg
                    QtyInBox = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 4, 0).ConvertintoSelectedUnit()
                    aa['QtyInBox'] = QtyInBox

                Orderdata['OrderNo'] = a
                '''Get Order Prifix '''
                b = GetPrifix.GetOrderPrifix(Division)
                Orderdata['FullOrderNumber'] = b+""+str(a)
                # return JsonResponse({ 'Data': Orderdata })
                Order_serializer = T_OrderSerializer(data=Orderdata)
                if Order_serializer.is_valid():
                    Order_serializer.save()
                    OrderID = Order_serializer.data['id']
                    PartyID = Order_serializer.data['Customer']
                    PartyMapping = M_Parties.objects.filter(
                        id=PartyID).values("SAPPartyCode")
                    if PartyMapping[0]['SAPPartyCode'] is None:
                        IsSAPCustomer = 0
                    else:
                        IsSAPCustomer = 1

                    #for log
                    if OrderType == 2:
                        log_entry = create_transaction_logNew(request, Orderdata, Orderdata['Supplier'],'From:'+Orderdata['POFromDate']+','+'To:'+Orderdata['POToDate']+','+'Supplier:'+str(Orderdata['Supplier'])+','+'TransactionID:'+str(OrderID),174,OrderID,Orderdata['POFromDate'],Orderdata['POToDate'],Orderdata['Customer'])
                    else:
                        log_entry = create_transaction_logNew(request, Orderdata, Orderdata['Customer'],'From:'+Orderdata['POFromDate']+','+'To:'+Orderdata['POToDate']+','+'TransactionID:'+str(OrderID),1,OrderID,Orderdata['POFromDate'],Orderdata['POToDate'],Orderdata['Supplier'])
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully', 'TransactionID': OrderID, 'OrderID': OrderID,  'IsSAPCustomer': IsSAPCustomer, 'Data': []})
                log_entry = create_transaction_logNew(request, Orderdata, 0, 'OrderSave:'+str(Order_serializer.errors),34,0)
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'OrderSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                OrderQuery = T_Orders.objects.filter(id=id)
                if OrderQuery.exists():
                    OrderSerializedata = T_OrderSerializerThird(
                        OrderQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata})
                    OrderData = list()
                    for a in OrderSerializedata:

                        OrderTermsAndCondition = list()
                        for b in a['OrderTermsAndConditions']:
                            OrderTermsAndCondition.append({
                                "id": b['TermsAndCondition']['id'],
                                "TermsAndCondition": b['TermsAndCondition']['Name'],
                            })

                        OrderItemDetails = list()
                        for b in a['OrderItem']:
                            if(b['IsDeleted'] == 0):
                                
                                aaaa = UnitwiseQuantityConversion(
                                    b['Item']['id'], b['Quantity'], b['Unit']['id'], 0, 0, 0, 1).GetConvertingBaseUnitQtyBaseUnitName()
                                
                                if (aaaa == b['Unit']['UnitID']['Name']):
                                    bb=''
                                else:
                                    bb=aaaa
                                
                                OrderItemDetails.append({
                                    "id": b['id'],
                                    "Item": b['Item']['id'],
                                    "ItemName": b['Item']['Name'],
                                    "ItemSAPCode": b['Item']['SAPItemCode'],
                                    "Quantity": b['Quantity'],
                                    "QuantityInNo": UnitwiseQuantityConversion(b['Item']['id'], b['Quantity'], b['Unit']['id'], 0, 0, 1, 1).ConvertintoSelectedUnit(),
                                    "MRP": b['MRP']['id'],
                                    "MRPValue": b['MRP']['MRP'],
                                    "Rate": b['Rate'],
                                    "Unit": b['Unit']['id'],
                                    "PrimaryUnitName":b['Unit']['UnitID']['Name'],
                                    "UnitName": bb,
                                    "SAPUnitName": b['Unit']['UnitID']['SAPUnit'],
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
                                    "DiscountType":b['DiscountType'],
                                    "Discount":b['Discount'],
                                    "DiscountAmount":b['DiscountAmount'],
                                    "Comment": b['Comment'],
                                })
                        
                        inward = 0
                        for c in a['OrderReferences']:
                            if(c['Inward'] == 1):
                                inward = 1
                        Address = GetPartyAddressDetails(
                            a['Supplier']['id']).PartyAddress()
                        OrderData.append({
                            "id": a['id'],
                            "OrderDate": a['OrderDate'],
                            "DeliveryDate": a['DeliveryDate'],
                            "OrderNo": a['OrderNo'],
                            "FullOrderNumber": a['FullOrderNumber'],
                            "POFromDate": a['POFromDate'],
                            "POToDate": a['POToDate'],
                            "POType": a['POType']['id'],
                            "POTypeName": a['POType']['Name'],
                            "OrderAmount": a['OrderAmount'],
                            "Description": a['Description'],
                            "Customer": a['Customer']['id'],
                            "CustomerSAPCode": a['Customer']['SAPPartyCode'],
                            "CustomerName": a['Customer']['Name'],
                            "CustomerGSTIN":a['Customer']['GSTIN'],
                            "Supplier": a['Supplier']['id'],
                            "SupplierSAPCode": a['Supplier']['SAPPartyCode'],
                            "SupplierName": a['Supplier']['Name'],
                            "SupplierGSTIN":a['Supplier']['GSTIN'],
                            "SupplierFssai": Address[0]['FSSAINo'],
                            "SupplierAddress": Address[0]['Address'],
                            "SupplierPIN": Address[0]['Pin'],
                            "BillingAddressID": a['BillingAddress']['id'],
                            "BillingAddress": a['BillingAddress']['Address'],
                            "BillingFssai": a['BillingAddress']['FSSAINo'],
                            "ShippingAddressID": a['ShippingAddress']['id'],
                            "ShippingAddress": a['ShippingAddress']['Address'],
                            "ShippingFssai": a['ShippingAddress']['FSSAINo'],
                            "Inward": inward,
                            "CreatedOn":a['CreatedOn'],
                            "OrderItem": OrderItemDetails,
                            "OrderTermsAndCondition": OrderTermsAndCondition
                        })
                    log_entry = create_transaction_logNew(request, {'OrderID':id}, a['Supplier']['id'],'From:'+a['POFromDate']+','+'To:'+a['POToDate']+','+'Supplier:'+str(a['Supplier']['id']),62,id,a['POFromDate'],a['POToDate'],a['Customer']['id'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData[0]})
                log_entry = create_transaction_logNew(request, {'OrderID':id}, a['Supplier']['id'], 'Order Not Found',62,0,0,0,a['Customer']['id'])
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'SingleOrder:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Orderupdatedata = JSONParser().parse(request)
                OrderupdateByID = T_Orders.objects.get(id=id)
                
                for aa in Orderupdatedata['OrderItem']:

                    BaseUnitQuantity = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 0, 0).GetBaseUnitQuantity()
                    aa['BaseUnitQuantity'] = BaseUnitQuantity
                    QtyInNo = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 1, 0).ConvertintoSelectedUnit()
                    aa['QtyInNo'] = QtyInNo
                    QtyInKg = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 2, 0).ConvertintoSelectedUnit()
                    aa['QtyInKg'] = QtyInKg
                    QtyInBox = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 4, 0).ConvertintoSelectedUnit()
                    aa['QtyInBox'] = QtyInBox

                # print(Orderupdatedata)
                Orderupdate_Serializer = T_OrderSerializer(
                    OrderupdateByID, data=Orderupdatedata)
                if Orderupdate_Serializer.is_valid():
                    Orderupdate_Serializer.save()
                    log_entry = create_transaction_logNew(request, Orderupdatedata, Orderupdatedata['Customer'],'From:'+Orderupdatedata['POFromDate']+','+'To:'+Orderupdatedata['POToDate']+','+'TransactionID:'+str(id),2,id,Orderupdatedata['POFromDate'],Orderupdatedata['POToDate'],Orderupdatedata['Supplier'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, Orderupdatedata, 0,'OrderEdit:'+str(Orderupdate_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Orderupdate_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'OrderEdit:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Order_Data = T_Orders.objects.get(id=id)
                Order_Data.delete()
                log_entry = create_transaction_logNew(request, {'OrderID':id}, 0, 'Order Deleted Successfully',3,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully', 'Data': []})
        except T_Orders.DoesNotExist:
            log_entry = create_transaction_logNew(request, {'OrderID':id}, 0, 'Order Not Found',3,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, {'OrderID':id}, 0, 'This Transaction used in another table',8,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'OrderDelete:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class EditOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request):

        try:
            with transaction.atomic():
                # DivisionID = request.data['Division']
                Party = request.data['Party']  # Order Page Supplier DropDown
                # Order Page Login Customer
                Customer = request.data['Customer']
                # Who's Rate you want
                RateParty = request.data['RateParty']
                EffectiveDate = request.data['EffectiveDate']
                OrderID = request.data['OrderID']
                OrderType = request.data['OrderType']
                q1 = M_Parties.objects.filter(id=Customer).values('PartyType')
                q2 = M_PartyType.objects.filter(
                    id=q1[0]['PartyType']).values('IsRetailer', 'IsSCM')
                if(OrderType==1):
                        Stockparty=Customer
                else:
                        Stockparty=Party
                # Is Not Retailer but is SSDD Order
               
                if (q2[0]['IsRetailer'] == 0 ):
                    PartyItem = Customer
                    
                    Itemquery = TC_OrderItems.objects.raw('''select a.Item id, a.Item_id,M_Items.Name ItemName,a.Quantity,a.Rate,a.Unit_id,M_Units.Name UnitName,a.BaseUnitQuantity,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,1) else a.GST_id end),SIGNED)GST_id,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,2) else M_GSTHSNCode.GSTPercentage  end),DECIMAL(10, 2))GSTPercentage,
                    (Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,3) else M_GSTHSNCode.HSNCode end)HSNCode,
                    convert((Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,1,0,0) else a.MRP_id end),SIGNED)MRP_id,
                            (Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,2,0,0) else M_MRPMaster.MRP  end)MRPValue,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,1,%s,%s) else a.Discount  end),DECIMAL(10, 2))Discount,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,2,%s,%s) else a.DiscountType  end),SIGNED)DiscountType,

a.Margin_id,M_MarginMaster.Margin MarginValue,a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,a.Comment,M_Items.Sequence ,M_Items.SAPItemCode,M_Units.SAPUnit SAPUnitName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,a.DiscountAmount
,
(select ifnull(sum(BaseUnitQuantity),0) from O_BatchWiseLiveStock where IsDamagePieces=0 and Item_id=a.Item_id 
and Party_id=%s 
group by Item_id)StockQuantity                
                from
(select * from (SELECT MC_PartyItems.Item_id FROM `MC_PartyItems` JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=MC_PartyItems.Item_id 
WHERE `MC_PartyItems`.`Party_id` = %s AND MC_PartyItems.Item_id in (SELECT `Item_id` FROM `MC_PartyItems` WHERE `MC_PartyItems`.`Party_id` = %s) and 
 M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id FROM MC_PartySubParty JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id 
 WHERE ( SubParty_id=%s)) and M_ChannelWiseItems.IsAvailableForOrdering=0 )b 
left join

(SELECT `Item_id` Item,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`,`Comment`,DiscountType,Discount,DiscountAmount
FROM `TC_OrderItems` WHERE (`TC_OrderItems`.`IsDeleted` = False AND `TC_OrderItems`.`Order_id` = %s))c
on b.Item_id=c.Item )a


INNER join M_Items on M_Items.id=Item_id 
left join M_MRPMaster on M_MRPMaster.id =a.MRP_id
left join MC_ItemUnits on MC_ItemUnits.id=a.Unit_id
left join M_Units on M_Units.id=MC_ItemUnits.UnitID_id
left join M_GSTHSNCode on M_GSTHSNCode.id=a.GST_id
left join M_MarginMaster on M_MarginMaster.id=a.Margin_id
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
Order By M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence''', ([EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[Customer],[Party],[EffectiveDate],[Customer],[Party],[Stockparty],[PartyItem], [Party],[PartyItem], [OrderID]))
                else:
                    PartyItem = Party
                    Itemquery = TC_OrderItems.objects.raw('''select a.Item id, a.Item_id,M_Items.Name ItemName,a.Quantity,a.Rate,a.Unit_id,M_Units.Name UnitName,a.BaseUnitQuantity,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,1) else a.GST_id end),SIGNED)GST_id,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,2) else M_GSTHSNCode.GSTPercentage  end),DECIMAL(10, 2))GSTPercentage,
                    (Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,3) else M_GSTHSNCode.HSNCode end)HSNCode,
                    convert((Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,1,0,0) else a.MRP_id end),SIGNED)MRP_id,
                            (Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,2,0,0) else M_MRPMaster.MRP  end)MRPValue,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,1,%s,%s) else a.Discount  end),DECIMAL(10, 2))Discount,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,2,%s,%s) else a.DiscountType  end),SIGNED)DiscountType,

a.Margin_id,M_MarginMaster.Margin MarginValue,a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,a.Comment,M_Items.Sequence ,M_Items.SAPItemCode,M_Units.SAPUnit SAPUnitName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,a.DiscountAmount
,(select ifnull(sum(BaseUnitQuantity),0) from O_BatchWiseLiveStock where IsDamagePieces=0 and Item_id=a.Item_id 
and Party_id=%s 
group by Item_id)StockQuantity                
                from
(select * from (SELECT `Item_id` FROM `MC_PartyItems` WHERE `MC_PartyItems`.`Party_id` = %s)b 
left join

(SELECT `Item_id` Item,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`, `Comment`,DiscountType,Discount,DiscountAmount
FROM `TC_OrderItems` WHERE (`TC_OrderItems`.`IsDeleted` = False AND `TC_OrderItems`.`Order_id` = %s))c
on b.Item_id=c.Item )a


INNER join M_Items on M_Items.id=Item_id 
left join M_MRPMaster on M_MRPMaster.id =a.MRP_id
left join MC_ItemUnits on MC_ItemUnits.id=a.Unit_id
left join M_Units on M_Units.id=MC_ItemUnits.UnitID_id
left join M_GSTHSNCode on M_GSTHSNCode.id=a.GST_id
left join M_MarginMaster on M_MarginMaster.id=a.Margin_id 
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
Order By M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence''', ([EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[Customer],[Party],[EffectiveDate],[Customer],[Party],[Stockparty],[PartyItem], [OrderID]))
                # print(Itemquery.query)
                OrderItemSerializer = OrderEditserializer(Itemquery, many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  '', 'Data': OrderItemSerializer})
                for b in OrderItemSerializer:
                    ItemID = b['Item_id']
                    GSTID = b['GST_id']
                    # print('**********************',ItemID)
                    
                    # =====================GST================================================
                    # if GSTID is None:
                    #     Gst = GSTHsnCodeMaster(
                    #         ItemID, EffectiveDate).GetTodaysGstHsnCode()
                    #     b['GST_id'] = Gst[0]['Gstid']
                    #     b['GSTPercentage'] = Gst[0]['GST']
                    #     # print('ttttttGST',Gst[0]['GST'])
                    

                    # =====================Current MRP================================================
                    # TodaysMRP = MRPMaster(
                    #     ItemID, 0, 0, EffectiveDate).GetTodaysDateMRP()

                    # b['MRP_id'] = TodaysMRP[0]['Mrpid']
                    # b['MRPValue'] = TodaysMRP[0]['TodaysMRP']
                    # print('ttttttttttMRP',TodaysMRP[0]['TodaysMRP'])
                    # =====================Current Discount================================================
                    # TodaysDiscount = DiscountMaster(
                    #     ItemID, Party, EffectiveDate,Customer).GetTodaysDateDiscount()

                    # b['DiscountType'] = 0
                    # b['Discount'] = 0
                    # print('ttttttttttDiscount',TodaysDiscount)
                    # =====================Rate================================================

                    # ratequery = TC_OrderItems.objects.filter(
                    #     Item_id=ItemID).values('Rate').order_by('-id')[:1]
                    # if not ratequery:
                    #     r = 0.00
                    # else:
                    #     r = ratequery[0]['Rate']

                    # if b['Rate'] is None:
                    #     b['Rate'] = r
                    # =====================Unit================================================
                    # UnitDetails = list()
                    # ItemUnitquery = MC_ItemUnits.objects.filter(
                    #     Item=ItemID, IsDeleted=0)
                    # ItemUnitqueryserialize = Mc_ItemUnitSerializerThird(
                    #     ItemUnitquery, many=True).data

                    # RateMcItemUnit = ""
                    # for d in ItemUnitqueryserialize:
                    #     if (d['PODefaultUnit'] == True):
                    #         RateMcItemUnit = d['id']
                    #     print(0,ItemID,RateParty,0,0,d['id'])
                    #     CalculatedRateusingMRPMargin=RateCalculationFunction(0,ItemID,RateParty,0,0,d['id']).RateWithGST()
                    #     UnitDetails.append({
                    #         "UnitID": d['id'],
                    #         "UnitName": d['BaseUnitConversion'] ,
                    #         "BaseUnitQuantity": d['BaseUnitQuantity'],
                    #         "PODefaultUnit": d['PODefaultUnit'],
                    #         "SODefaultUnit": d['SODefaultUnit'],
                    #         "Rate" : CalculatedRateusingMRPMargin[0]["RateWithoutGST"]

                    #     })

                    # =====================IsDefaultTermsAndConditions================================================

                    b.update({  #"StockQuantity": Stock,
                              "UnitDetails": UnitDropdown(ItemID, RateParty, 0)
                              })

                    # bomquery = MC_BillOfMaterialItems.objects.filter(
                    #     Item_id=ItemID, BOM__IsVDCItem=1).select_related('BOM')
                    # if bomquery.exists():
                    b.update({"Bom": True})
                    # else:
                    #     b.update({"Bom": False})

                if OrderID != 0:
                    OrderQuery = T_Orders.objects.get(id=OrderID)
                    a = T_OrderSerializerThird(OrderQuery).data

                    OrderTermsAndCondition = list()
                    for b in a['OrderTermsAndConditions']:
                        # print(b['TermsAndCondition']['IsDeleted'])
                        if b['IsDeleted'] == 0:
                            OrderTermsAndCondition.append({
                                "id": b['TermsAndCondition']['id'],
                                "TermsAndCondition": b['TermsAndCondition']['Name'],
                            })
                    inward = 0
                    for c in a['OrderReferences']:
                        if(c['Inward'] == 1):
                            inward = 1

                    OrderData = list()
                    OrderData.append({
                        "id": a['id'],
                        "OrderDate": a['OrderDate'],
                        "DeliveryDate": a['DeliveryDate'],
                        "POFromDate": a['POFromDate'],
                        "POToDate": a['POToDate'],
                        "POType": a['POType']['id'],
                        "POTypeName": a['POType']['Name'],
                        "OrderAmount": a['OrderAmount'],
                        "Description": a['Description'],
                        "Customer": a['Customer']['id'],
                        "CustomerSAPCode": a['Customer']['SAPPartyCode'],
                        "CustomerName": a['Customer']['Name'],
                        "Supplier": a['Supplier']['id'],
                        "SupplierSAPCode": a['Supplier']['SAPPartyCode'],
                        "SupplierName": a['Supplier']['Name'],
                        "BillingAddressID": a['BillingAddress']['id'],
                        "BillingAddress": a['BillingAddress']['Address'],
                        "ShippingAddressID": a['ShippingAddress']['id'],
                        "ShippingAddress": a['ShippingAddress']['Address'],
                        "BillingAddress": a['BillingAddress']['Address'],
                        "ShippingAddressID": a['ShippingAddress']['id'],
                        "ShippingAddress": a['ShippingAddress']['Address'],
                        "Inward": inward,
                        "CustomerGSTIN": a['Customer']['GSTIN'],
                        "SupplierGSTIN": a['Supplier']['GSTIN'],
                        "OrderItems": OrderItemSerializer,
                        "TermsAndConditions": OrderTermsAndCondition,
                        "CreatedBy":a['CreatedBy'],
                        "CreatedOn":a['CreatedOn']
                    })
                    FinalResult = OrderData[0]

                else:

                    TermsAndConditions = list()
                    TermsAndConditionsquery = M_TermsAndConditions.objects.filter(
                        IsDefault=1)
                    TermsAndConditionsSerializer = M_TermsAndConditionsSerializer(
                        TermsAndConditionsquery, many=True).data

                    for d in TermsAndConditionsSerializer:
                        TermsAndConditions.append({
                            "id": d['id'],
                            "TermsAndCondition": d['Name']
                        })

                    NewOrder = list()
                    NewOrder.append({
                        "id": "",
                        "OrderDate": "",
                        "DeliveryDate": "",
                        "POFromDate": "",
                        "POToDate": "",
                        "POType": "",
                        "POTypeName": "",
                        "OrderAmount": "",
                        "Description": "",
                        "Customer": "",
                        "CustomerName": "",
                        "Supplier": "",
                        "SupplierName": "",
                        "BillingAddressID": "",
                        "BillingAddress": "",
                        "ShippingAddressID": "",
                        "ShippingAddress": "",
                        "Inward": "",
                        "CustomerGSTIN": "",
                        "SupplierGSTIN": "",
                        "OrderItems": OrderItemSerializer,
                        "TermsAndConditions": TermsAndConditions,
                        "CreatedBy":"",
                        "CreatedOn":""
                    })

                    FinalResult = NewOrder[0]
                # log_entry = create_transaction_logNew(request, {'OrderID':OrderID}, Party,'From:'+a['POFromDate']+','+'To:'+a['POToDate'],2,0,a['POFromDate'],a['POToDate'],Customer)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  '', 'Data': FinalResult})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'EditOrder:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})


class ConfirmOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                POOrderIDs = Orderdata['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderItemQuery = T_Orders.objects.filter(
                    id__in=Order_list).update(IsConfirm=1)
                log_entry = create_transaction_logNew(request, Orderdata, 0, "Orders Data Confirm Successfully",30,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Orders Data Confirm Successfully ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'OrderConfirm:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class SummaryReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():

                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Company = Orderdata['CompanyID']
                Party = Orderdata['PartyID']
                Employee = Orderdata['Employee']
                OrderType = Orderdata['OrderType']

                q0 = MC_SettingsDetails.objects.filter(
                        SettingID=1, Company=Company).values('Value')
                v=q0[0]["Value"]
                pricelist =v.split(",")

                if Employee > 0:
                    EmpPartys=MC_EmployeeParties.objects.raw('''select EmployeeParties(%s) id''',[Employee])
                    for row in EmpPartys:
                        p=row.id
                    PartyIDs = p.split(",")
                
                # OrderQuery='''SELECT T_Orders.id ,T_Orders.FullOrderNumber OrderNo,M_Group.name GroupName,MC_SubGroup.Name SubGroup,M_Items.Name MaterialName,OrderDate,s.Name SupplierName,c.Name CustomerName,TC_OrderItems.QtyInNo,TC_OrderItems.QtyInKg,TC_OrderItems.QtyInBox,TC_OrderItems.Amount,T_Orders.OrderAmount,T_Orders.CreatedOn  FROM T_Orders left join TC_InvoicesReferences on TC_InvoicesReferences.Order_id=T_Orders.id join TC_OrderItems on T_Orders.id=TC_OrderItems.Order_id join M_Items on M_Items.id=TC_OrderItems.Item_id join M_Parties s on T_Orders.Supplier_id=s.id join M_Parties c on T_Orders.Customer_id=c.id left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id where TC_InvoicesReferences.Order_id is null and OrderDate between %s and %s and c.PriceList_id in %s'''
                OrderQuery='''SELECT T_Orders.id ,T_Orders.FullOrderNumber OrderNo,M_Group.name GroupName,MC_SubGroup.Name SubGroup,M_Items.Name MaterialName,OrderDate,s.Name SupplierName,c.Name CustomerName,TC_OrderItems.QtyInNo,TC_OrderItems.QtyInKg,TC_OrderItems.QtyInBox,TC_OrderItems.Amount,T_Orders.OrderAmount,T_Orders.CreatedOn  
                FROM T_Orders 
                left join TC_InvoicesReferences on TC_InvoicesReferences.Order_id=T_Orders.id and TC_InvoicesReferences.Order_id is null
                join TC_OrderItems on T_Orders.id=TC_OrderItems.Order_id 
                join M_Items on M_Items.id=TC_OrderItems.Item_id 
                join M_Parties s on T_Orders.Supplier_id=s.id 
                join M_Parties c on T_Orders.Customer_id=c.id 
                left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id 
                left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
                where  OrderDate between %s and %s''' 

                if OrderType == 1:
                    if Party == "":
                        OrderQuery += " "
                        x = 0
                        if Employee == 0:
                            OrderQuery += " "
                        else:
                            OrderQuery += " and Customer_id in %s"
                    else:
                        OrderQuery += " and Customer_id=%s"
                        x = Party
                        
                else:
                    if Party == "":
                        OrderQuery += " "
                        x = 0
                        if Employee == 0:
                            OrderQuery += " "
                        else:
                            OrderQuery += " and Supplier_id in %s"
                    else:
                        OrderQuery += " and Supplier_id=%s"
                        x = Party

                if Party != "" and Employee >0:
                        # OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,pricelist,Party])
                        OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,Party])
                        
                elif Party != "":
                        # OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,pricelist,Party])
                        OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,Party])
                        
                elif Employee >0:
                        # OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,pricelist, PartyIDs])
                        OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,PartyIDs])
                    
                else:
                        # OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,pricelist])  
                        OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate])   
                # print(OrderQueryresults.query)
                if OrderQuery:
                    OrderItemDetails = list()
                    for row in OrderQueryresults:
                        OrderItemDetails.append({
                            "id": row.id,
                            "OrderNo": row.OrderNo,
                            "OrderDate": row.OrderDate,
                            "SupplierName": row.SupplierName,
                            "CustomerName": row.CustomerName,
                            "GroupName": row.GroupName,
                            "SubGroup": row.SubGroup,
                            "MaterialName": row.MaterialName,
                            "QtyInNo": float(row.QtyInNo),
                            "QtyInKg": float(row.QtyInKg),
                            "QtyInBox": float(row.QtyInBox),
                            "OrderAmount": float(row.OrderAmount),
                            "CreatedOn": row.CreatedOn

                            
                        })
                    log_entry = create_transaction_logNew(request, Orderdata, x, 'From:'+FromDate+','+'To:'+ToDate,31,0,FromDate,ToDate,0)            
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemDetails})
                log_entry = create_transaction_logNew(request, Orderdata, x, "Order Summary Not available",31,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'OrderSummaryReport:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})


class TestOrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                OrderQuery = T_Orders.objects.filter(id=id)
                if OrderQuery.exists():
                    OrderSerializedata = TestOrderSerializer(
                        OrderQuery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderSerializedata})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
