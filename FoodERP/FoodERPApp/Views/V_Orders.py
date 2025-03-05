from django.http import JsonResponse
from django.db.models import F, Q
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
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models import Value, CharField
from ..models import *
from django.db.models import F

class POTypeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PoTypedata = M_POType.objects.all()
                if PoTypedata.exists():
                    PoTypedata_serializer = M_POTypeserializer(PoTypedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PoTypedata_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'POType Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


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
                Country = Orderdata['Country']

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
                
                    if Country:
                        bbb = Q(Customer__PartyType__Country_id=Country)
                    else:
                        bbb = Q()

                    if(CustomerType == ''):  # all
                        aaa = Q()
                    else:
                        CustomerType_list = CustomerType.split(",")
                        aaa = Q(Customer__PriceList_id__in=CustomerType_list)

                    if(Customer == ''):
                        q0 = MC_PartySubParty.objects.filter(Party=Supplier).values('SubParty')
                        q1 = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Supplier_id=Supplier,Customer_id__in=q0).select_related('Customer').filter(aaa,bbb)
                        query = T_Orders.objects.filter(
                            OrderDate__range=[FromDate, ToDate], Supplier_id=Supplier).select_related('Customer').filter(aaa,bbb)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=FromDate, POToDate__gte=ToDate, Supplier_id=Supplier).select_related('Customer').filter(aaa,bbb)
                        q2 = query.union(queryForOpenPO)
                        q = q2.union(q1)

                    else:
                        query = T_Orders.objects.filter(OrderDate__range=[
                                                        FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier).select_related('Customer').filter(aaa,bbb)
                        queryForOpenPO = T_Orders.objects.filter(
                            POFromDate__lte=FromDate, POToDate__gte=ToDate, Customer_id=Customer, Supplier_id=Supplier).select_related('Customer').filter(aaa,bbb)
                        q = query.union(queryForOpenPO)
                # CustomPrint(query.query)
                # return JsonResponse({'query': str(q.query)})
                if q:
                    Order_serializer = T_OrderSerializerSecond(
                        q, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    OrderListData = list()
                    for a in Order_serializer:

                        SubPartyFlagquery = MC_PartySubParty.objects.filter(Party=a['Supplier']['id'],SubParty=a['Customer']['id']).values('SubParty')

                        if SubPartyFlagquery:
                            SubPartyFlag= True
                        else:
                            SubPartyFlag= False
                        
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
                                   
                            PartyTypeID = a['Supplier']['PartyType']['id'] if a['Supplier']['PartyType'] else None                  
                           
                            if PartyTypeID == 19:
                                Count = TC_SPOSInvoicesReferences.objects.filter(Order=a['id']).count()
                            else:
                                Count = TC_InvoicesReferences.objects.filter(Order=a['id']).count()

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
                                "MobileAppOrderFlag" : a['MobileAppOrderFlag'],
                                "AdvanceAmount": a['AdvanceAmount'],
                                "SubPartyFlag": SubPartyFlag
                                
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
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Supplier = Orderdata['Supplier']
                OrderType = Orderdata['OrderType']
                Percentage=""

                d = date.today()

                #for log
                if OrderType == 3:
                    
                    if (Supplier == ''):
                        supplier = 0
                        customer=Customer
                    else:
                        supplier = Supplier
                        customer=0
                else:
                    
                    if (Customer == ''):
                        customer = 0
                        supplier=Supplier
                    else:
                        customer= Customer
                        supplier=0
                    

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
                        log_entry = create_transaction_logNew(request, Orderdata, customer,'From:'+FromDate+','+'To:'+ToDate,28,0,FromDate,ToDate,supplier)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                    log_entry = create_transaction_logNew(request, Orderdata, customer, "Order List Not Found",28,0,FromDate,ToDate,supplier)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})

                elif(OrderType == 1):  # OrderType -1 PO Order
                    # CustomPrint("FDFDFDFD")
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
                        # CustomPrint("First Query SQL:")
                        # CustomPrint(query.query)
                        # CustomPrint("Second Query SQL:")
                        # CustomPrint(queryForOpenPO.query)
                        # CustomPrint("Combined Query SQL:")
                        # CustomPrint(q.query)
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

                # Challanquery = T_Challan.objects.filter(Party=Customer)
                # Challan_serializer = ChallanSerializerList(
                #     Challanquery, many=True).data
                # for a in Challan_serializer:
                #     Query = TC_GRNReferences.objects.filter(
                #         Challan_id=a['id']).select_related('GRN').values('GRN_id')
                #     GRNList = list()
                #     for b in Query:
                #         GRNList.append(b['GRN_id'])
                #         if not GRNList:
                #             Percentage = 0
                #         else:
                #             y = tuple(GRNList)
                #             Itemsquery = TC_GRNItems.objects.filter(
                #                 GRN__in=y).aggregate(Sum('Quantity'))
                #             Percentage = (
                #                 float(Itemsquery['Quantity__sum'])/float(a['ChallanItems'][0]['Quantity']))*100

                #     OrderListData.append({
                #         "id": a['id'],
                #         "OrderDate": a['ChallanDate'],
                #         "DeliveryDate": "",
                #         "FullOrderNumber": a['FullChallanNumber'],
                #         "CustomerID": a['Customer']['id'],
                #         "Customer": a['Customer']['Name'],
                #         "SupplierID": a['Party']['id'],
                #         "Supplier": a['Party']['Name'],
                #         "OrderAmount": a['GrandTotal'],
                #         "Description": "",
                #         "OrderType": "",
                #         "POType": "Challan",
                #         "BillingAddress": "",
                #         "ShippingAddress": "",
                #         "CreatedBy": a['CreatedBy'],
                #         "CreatedOn": a['CreatedOn'],
                #         "Inward": "",
                #         "Percentage": Percentage,

                #     })
                log_entry = create_transaction_logNew(request, Orderdata, customer,'From:'+FromDate+','+'To:'+ToDate,28,0,FromDate,ToDate,supplier)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': OrderListData})
            log_entry = create_transaction_logNew(request, Orderdata, z, "Order Not available",28,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0,'OrderListSecond:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class T_OrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Division = Orderdata['Division']
                OrderType = Orderdata['OrderType']
                OrderDate = Orderdata['OrderDate']
                Supplier  = Orderdata['Supplier']
                AdvanceAmount =  Orderdata['AdvanceAmount']
                
                '''Get Max Order Number'''
                a = GetMaxNumber.GetOrderNumber(Supplier, OrderType, OrderDate)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                
                for aa in Orderdata['OrderItem']:

                    BaseUnitQuantity = UnitwiseQuantityConversion(
                        aa['Item'], aa['Quantity'], aa['Unit'], 0, 0, 0, 0).GetBaseUnitQuantity()
                    aa['BaseUnitQuantity'] = round(BaseUnitQuantity,3)
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
                Orderdata['AdvanceAmount'] = AdvanceAmount
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
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully', 'TransactionID': OrderID, 'OrderID': OrderID,  'IsSAPCustomer': IsSAPCustomer, 'AdvanceAmount': AdvanceAmount, 'Data': []})
                log_entry = create_transaction_logNew(request, Orderdata, 0, 'OrderSave:'+str(Order_serializer.errors),34,0)
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0,'OrderSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class T_OrdersPrintView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request):
        OrderData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                OrderIDs = OrderData['OrderIDs'].split(",")
                OrderData = []
                
                for id in OrderIDs:
                    OrderQuery = T_Orders.objects.filter(id=id)
                    if OrderQuery.exists():
                        OrderSerializedata = T_OrderSerializerThird(OrderQuery, many=True).data
                        for a in OrderSerializedata:
                            OrderTermsAndCondition = []
                            for b in a['OrderTermsAndConditions']:
                                OrderTermsAndCondition.append({
                                    "id": b['TermsAndCondition']['id'],
                                    "TermsAndCondition": b['TermsAndCondition']['Name'],
                                })

                        OrderItemDetails = []
                        for b in a['OrderItem']:
                            # CustomPrint(b)
                            if(b['IsDeleted'] == 0):
                                
                                # aaaa = UnitwiseQuantityConversion(
                                #     b['Item']['id'], b['Quantity'], b['Unit']['id'], 0, 0, 0, 1).GetConvertingBaseUnitQtyBaseUnitName()
                                
                                # if (aaaa == b['Unit']['UnitID']['Name']):
                                #     bb=''
                                # else:
                                #     bb=aaaa

                                q = M_Parties.objects.filter(id=a['Customer']['id'],PartyType=a['Customer']['PartyType']).select_related(
                                'PartyType').annotate(IsFranchises=F('PartyType__IsFranchises')).values('IsFranchises')
                                if q[0]['IsFranchises'] != 0:
                                    GroupTypeID = 5
                                else:
                                    GroupTypeID = 1
                                q1 = MC_ItemGroupDetails.objects.filter(GroupType=GroupTypeID, Item=b['Item']['id']
                                ).select_related('Group', 'SubGroup').annotate(
                                    GroupName=F('Group__Name'),
                                    SubGroupName=F('SubGroup__Name'),
                                    GroupSequences =F('Group__Sequence'),
                                    SubGroupSequences = F('SubGroup__Sequence'),
                                    ItemSequences = F('ItemSequence')).order_by('Group__Sequence', 'SubGroup__Sequence','ItemSequence').values('GroupName', 'SubGroupName','GroupSequences','SubGroupSequences','ItemSequences')
                                # print(q1.query)
                                if q1.exists():
                                    Group = q1[0]['GroupName']
                                    SubGroup = q1[0]['SubGroupName']
                                    GroupSequence =q1[0]['GroupSequences']
                                    SubGroupSequence = q1[0]['SubGroupSequences']
                                    ItemSequence = q1[0]['ItemSequences']
                                else:                              
                                    Group = ""
                                    SubGroup = ""
                                    GroupSequence =""
                                    SubGroupSequence = ""
                                    ItemSequence= ""
                               
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
                                    "UnitName":  b['Unit']['BaseUnitConversion'],
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
                                    "IsHighlightItemInPrint" : b['OrderItem'],
                                    "Group": Group,
                                    "SubGroup": SubGroup,
                                    "GroupSequence" : GroupSequence,
                                    "SubGroupSequence" : SubGroupSequence,
                                    "ItemSequence" : ItemSequence
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
                            "AdvanceAmount": a['AdvanceAmount'],
                            "Description": a['Description'],
                            "SAPOrderNo" :  a['SAPResponse'],
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
                    else:
                        continue

                if OrderData:
                    log_entry = create_transaction_logNew(request, OrderData, 0, "Orders Data Confirm Successfully",62,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData})
                else:
                    log_entry = create_transaction_logNew(request, OrderData, 0, "No Orders Found",62,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'No Orders Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, OrderData, 0,'Orders:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e)})

class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    def put(self, request, id=0):
        Orderupdatedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
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

                # CustomPrint(Orderupdatedata)
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
            log_entry = create_transaction_logNew(request, Orderupdatedata, 0,'OrderEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

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
            log_entry = create_transaction_logNew(request, 0, 0,'OrderDelete:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class EditOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request):

        try:
            with transaction.atomic():
                # DivisionID = request.data['Division']
                Party = request.data['Party']  # Order Page Supplier DropDown
                Customer = request.data['Customer']     # Order Page Login Customer
                RateParty = request.data['RateParty']           # Who's Rate you want
                EffectiveDate = request.data['EffectiveDate']
                OrderID = request.data['OrderID']
                OrderType = request.data['OrderType']
                DemandID = request.data['Demand']
                
                q1 = M_Parties.objects.filter(id=Customer).select_related('PartyType').values('PartyType','PartyType__IsRetailer','PartyType__IsSCM','PartyType__IsFranchises')
                # q2 = M_PartyType.objects.filter(
                #     id=q1[0]['PartyType']).values('IsRetailer', 'IsSCM')
                if(OrderType == 1):
                        Stockparty=Customer
                else:
                        Stockparty=Party
                # Is Not Retailer but is SSDD Order
                
                if q1[0]['PartyType__IsFranchises'] == 1:
                        StockQuantity = (f'''(SELECT COALESCE(MAX(O_SPOSDateWiseLiveStock.ClosingBalance), 0)    FROM SweetPOS.O_SPOSDateWiseLiveStock
                                           Where O_SPOSDateWiseLiveStock.Item = a.Item_id 
                                              AND O_SPOSDateWiseLiveStock.Party = {Stockparty} AND O_SPOSDateWiseLiveStock.StockDate = CURDATE() ) AS StockQuantity''')
                else:
                        StockQuantity = (f''' (SELECT IFNULL(SUM(BaseUnitQuantity), 0) FROM O_BatchWiseLiveStock 
                                                    WHERE IsDamagePieces = 0 AND Item_id = a.Item_id AND Party_id = {Stockparty} GROUP BY Item_id) AS StockQuantity''')

                if (q1[0]['PartyType__IsRetailer'] == 0 ):
                    PartyItem = Customer
                    ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(Stockparty,0).split('!') 
                    
                    Itemquery = TC_OrderItems.objects.raw(f'''select a.Item id, a.Item_id,M_Items.Name ItemName,a.Quantity,a.Rate,a.Unit_id,M_Units.Name UnitName,a.BaseUnitQuantity,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,1,{RateParty},0) else a.GST_id end),SIGNED)GST_id,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,2,{RateParty},0) else M_GSTHSNCode.GSTPercentage  end),DECIMAL(10, 2))GSTPercentage,
                            (Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,3,{RateParty},0) else M_GSTHSNCode.HSNCode end)HSNCode,
                    convert((Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,1,0,{RateParty},0) else a.MRP_id end),SIGNED)MRP_id,
                            (Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,2,0,{RateParty},0) else M_MRPMaster.MRP  end)MRPValue,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,1,%s,%s) else a.Discount  end),DECIMAL(10, 2))Discount,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,2,%s,%s) else a.DiscountType  end),SIGNED)DiscountType,

a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,a.Comment,M_Items.Sequence ,M_Items.SAPItemCode,M_Units.SAPUnit SAPUnitName,
{ItemsGroupJoinsandOrderby[0]},
ifnull(a.DiscountAmount,0)DiscountAmount,
{StockQuantity}, Round(GetTodaysDateRate(a.Item_id, %s,%s,0,2),2) AS VRate,(select BaseUnitQuantity from MC_ItemUnits where IsDeleted=0  and UnitID_id=2 and Item_id=a.Item_id)Weightage                 
                from
(select * from 
    (SELECT MC_PartyItems.Item_id FROM `MC_PartyItems` 
    JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=MC_PartyItems.Item_id 
    WHERE `MC_PartyItems`.`Party_id` = %s 
    AND MC_PartyItems.Item_id in (SELECT `Item_id` FROM `MC_PartyItems` WHERE `MC_PartyItems`.`Party_id` = %s) 
    AND M_ChannelWiseItems.PartyType_id IN (SELECT PartyType_id FROM  M_Parties where id=%s) 
    AND M_ChannelWiseItems.IsAvailableForOrdering=0 )b 
    
    left join

    (SELECT `Item_id` Item,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`,`Comment`,DiscountType,Discount,DiscountAmount
    FROM `TC_OrderItems` WHERE `TC_OrderItems`.`IsDeleted` = False AND `TC_OrderItems`.`Order_id` = %s
                                                          
        union
    SELECT `Item_id` Item,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`,'' 'Comment','' DiscountType,'' Discount,0 DiscountAmount
    FROM `TC_DemandItems` WHERE `TC_DemandItems`.`IsDeleted` = False AND `TC_DemandItems`.Demand_id ={DemandID} )c
    on b.Item_id=c.Item 
)a


     join M_Items on M_Items.id=Item_id and IsCBMItem=1
left join M_MRPMaster on M_MRPMaster.id =a.MRP_id
left join MC_ItemUnits on MC_ItemUnits.id=a.Unit_id
left join M_Units on M_Units.id=MC_ItemUnits.UnitID_id
left join M_GSTHSNCode on M_GSTHSNCode.id=a.GST_id
{ItemsGroupJoinsandOrderby[1]} 
{ItemsGroupJoinsandOrderby[2]} ''', ([EffectiveDate], [EffectiveDate], [EffectiveDate], [EffectiveDate],
                                                           [EffectiveDate], [EffectiveDate], [Customer], [Party], [EffectiveDate], 
                                                           [Customer], [Party], [EffectiveDate], [RateParty], [PartyItem],
                                                           [Party], [PartyItem], [OrderID]))
                    
               
                else:
                    PartyItem = Party
                    ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(Stockparty,0).split('!') 
                    
                    Itemquery = TC_OrderItems.objects.raw(f'''select a.Item id, a.Item_id,M_Items.Name ItemName,a.Quantity,a.Rate,a.Unit_id,M_Units.Name UnitName,a.BaseUnitQuantity,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,1,{RateParty},0) else a.GST_id end),SIGNED)GST_id,
                    convert((Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,2,{RateParty},0) else M_GSTHSNCode.GSTPercentage  end),DECIMAL(10, 2))GSTPercentage, 
                    (Case when a.GST_id is null then GSTHsnCodeMaster(a.Item_id,%s,3,{RateParty},0) else M_GSTHSNCode.HSNCode end)HSNCode,
                    convert((Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,1,0,{RateParty},0) else a.MRP_id end),SIGNED)MRP_id,
                            (Case when a.MRP_id is null then GetTodaysDateMRP(a.Item_id,%s,2,0,{RateParty},0) else M_MRPMaster.MRP  end)MRPValue,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,1,%s,%s) else a.Discount  end),DECIMAL(10, 2))Discount,
                    convert((Case when a.Discount is null then GetTodaysDateDiscount(a.Item_id,%s,2,%s,%s) else a.DiscountType  end),SIGNED)DiscountType,

a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,a.Comment,M_Items.Sequence ,M_Items.SAPItemCode,M_Units.SAPUnit SAPUnitName,
{ItemsGroupJoinsandOrderby[0]},
ifnull(a.DiscountAmount,0)DiscountAmount,
{StockQuantity},
Round(GetTodaysDateRate(a.Item_id, '{EffectiveDate}','{Party}',0,2),2) AS VRate,(select BaseUnitQuantity from MC_ItemUnits where IsDeleted=0  and UnitID_id=2 and Item_id=a.Item_id)Weightage            
                from
(select * from 
        (SELECT `Item_id` FROM `MC_PartyItems` WHERE `MC_PartyItems`.`Party_id` = %s)b 
    left join

        (SELECT `Item_id` Item,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`, `Comment`,DiscountType,Discount,DiscountAmount
        FROM `TC_OrderItems` WHERE `TC_OrderItems`.`IsDeleted` = False AND `TC_OrderItems`.`Order_id` = %s
        
            union
    SELECT `Item_id` Item,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`,'' 'Comment','' DiscountType,'' Discount,0 DiscountAmount
    FROM `TC_DemandItems` WHERE `TC_DemandItems`.`IsDeleted` = False AND `TC_DemandItems`.Demand_id ={DemandID} )c
    on b.Item_id=c.Item 
)a


join M_Items on M_Items.id=Item_id and IsCBMItem=1
left join M_MRPMaster on M_MRPMaster.id =a.MRP_id
left join MC_ItemUnits on MC_ItemUnits.id=a.Unit_id
left join M_Units on M_Units.id=MC_ItemUnits.UnitID_id
left join M_GSTHSNCode on M_GSTHSNCode.id=a.GST_id
{ItemsGroupJoinsandOrderby[1]}
{ItemsGroupJoinsandOrderby[2]}''', ([EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[EffectiveDate],[Customer],
                                    [Party],[EffectiveDate],[Customer],[Party],[PartyItem], [OrderID]))
                
                OrderItemSerializer = OrderEditserializer(Itemquery, many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  '', 'Data': OrderItemSerializer})
                for b in OrderItemSerializer:
                    ItemID = b['Item_id']
                    
                    b.update({  #"StockQuantity": Stock,
                              "UnitDetails": UnitDropdown(ItemID, RateParty, 0)
                              })
                    
                    # bomquery = MC_BillOfMaterialItems.objects.filter(
                    #     Item_id=ItemID, BOM__IsVDCItem=1).select_related('BOM')
                    # if bomquery.exists():
                    b.update({"Bom": True})
                    # else:
                    #     b.update({"Bom": False})

                if (OrderID != 0 or DemandID != 0):
                    if(OrderID != 0):
                        OrderQuery = T_Orders.objects.filter(id=OrderID).select_related(
    'Supplier', 'Customer', 'POType', 'BillingAddress', 'ShippingAddress', 'OrderReferences'
).annotate(
    OrderReferences__Inward=Coalesce('OrderReferences__Inward', Value('0'), output_field=CharField())
).values(
    'id', 'OrderDate', 'DeliveryDate', 'POFromDate', 'POToDate', 'POType', 'POType__Name', 'OrderAmount',
    'Description', 'Customer', 'Customer__SAPPartyCode', 'Customer__Name', 'Supplier', 'Supplier__SAPPartyCode',
    'Supplier__Name', 'BillingAddress', 'BillingAddress__Address', 'ShippingAddress', 'ShippingAddress__Address',
    'Customer__GSTIN', 'Supplier__GSTIN', 'OrderReferences__Inward', 'CreatedBy', 'CreatedOn', 'OrderTermsAndConditions','AdvanceAmount'
)
                    else:  
                        
                        OrderQuery = T_Demands.objects.filter(id=DemandID).select_related(
    'Supplier', 'Customer', 'BillingAddress', 'ShippingAddress'

).annotate(
    OrderReferences__Inward=Value(0, output_field=CharField()),
    DeliveryDate=F('DemandDate'),
    POFromDate=Value(0, output_field=CharField()),
    POToDate=Value(0, output_field=CharField()),
    POType=Value(0, output_field=CharField()),
    POType__Name=Value('', output_field=CharField()),
    OrderTermsAndConditions=Value(0, output_field=CharField()),
    OrderDate=F('DemandDate'),
    OrderAmount=F('DemandAmount'),
    Description=F('Comment'),
).values(
    'id', 'OrderDate', 'DeliveryDate', 'POFromDate', 'POToDate', 'POType', 'POType__Name', 'OrderAmount',
    'Description', 'Customer', 'Customer__SAPPartyCode', 'Customer__Name', 'Supplier', 'Supplier__SAPPartyCode',
    'Supplier__Name', 'BillingAddress', 'BillingAddress__Address', 'ShippingAddress', 'ShippingAddress__Address',
    'Customer__GSTIN', 'Supplier__GSTIN','OrderReferences__Inward' , 'CreatedBy', 'CreatedOn', 'OrderTermsAndConditions','AdvanceAmount'
)
                    # print(OrderQuery)
                    OrderTermsAndConditionQuery=TC_OrderTermsAndConditions.objects.filter(Order = OrderID ,IsDeleted=0).select_related('TermsAndCondition').values('TermsAndCondition','TermsAndCondition__Name')
                    
                    OrderTermsAndCondition = list()
                    for b in OrderTermsAndConditionQuery:
                        OrderTermsAndCondition.append({
                            "id": b['TermsAndCondition'],
                            "TermsAndCondition": b['TermsAndCondition__Name'],
                        })
                    

                    OrderData = list()
                    OrderData.append({
                        "id": OrderQuery[0]['id'],
                        "OrderDate": OrderQuery[0]['OrderDate'],
                        "DeliveryDate": OrderQuery[0]['DeliveryDate'],
                        "POFromDate": OrderQuery[0]['POFromDate'],
                        "POToDate": OrderQuery[0]['POToDate'],
                        "POType": OrderQuery[0]['POType'],
                        "POTypeName": OrderQuery[0]['POType__Name'],
                        "OrderAmount": OrderQuery[0]['OrderAmount'],
                        "AdvanceAmount": OrderQuery[0]['AdvanceAmount'],
                        "Description": OrderQuery[0]['Description'],
                        "Customer": OrderQuery[0]['Customer'],
                        "CustomerSAPCode": OrderQuery[0]['Customer__SAPPartyCode'],
                        "CustomerName": OrderQuery[0]['Customer__Name'],
                        "Supplier": OrderQuery[0]['Supplier'],
                        "SupplierSAPCode": OrderQuery[0]['Supplier__SAPPartyCode'],
                        "SupplierName": OrderQuery[0]['Supplier__Name'],
                        "BillingAddressID": OrderQuery[0]['BillingAddress'],
                        "BillingAddress": OrderQuery[0]['BillingAddress__Address'],
                        "ShippingAddressID": OrderQuery[0]['ShippingAddress'],
                        "ShippingAddress": OrderQuery[0]['ShippingAddress__Address'],
                        "Inward": int(OrderQuery[0]['OrderReferences__Inward']),
                        "CustomerGSTIN": OrderQuery[0]['Customer__GSTIN'],
                        "SupplierGSTIN": OrderQuery[0]['Supplier__GSTIN'],
                        "OrderItems": OrderItemSerializer,
                        "TermsAndConditions": OrderTermsAndCondition,
                        "CreatedBy":OrderQuery[0]['CreatedBy'],
                        "CreatedOn":OrderQuery[0]['CreatedOn']
                        
                    })
                    FinalResult = OrderData[0]

                else:

                    TermsAndConditions = list()
                    TermsAndConditionsquery = M_TermsAndConditions.objects.filter(IsDefault=1).values('id','Name')
                    for d in TermsAndConditionsquery:
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
                        "AdvanceAmount": "",
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
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e) , 'Data': []})


class ConfirmOrderView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                POOrderIDs = Orderdata['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderItemQuery = T_Orders.objects.filter(
                    id__in=Order_list).update(IsConfirm=1)
                log_entry = create_transaction_logNew(request, Orderdata, 0, "Orders Data Confirm Successfully",30,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Orders Data Confirm Successfully ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0,'OrderConfirm:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class SummaryReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
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
                OrderQuery='''SELECT T_Orders.id ,T_Orders.FullOrderNumber OrderNo,M_Group.name GroupName,
                MC_SubGroup.Name SubGroup,M_Items.Name MaterialName,OrderDate,s.Name SupplierName,
                c.Name CustomerName, TC_OrderItems.QtyInNo,TC_OrderItems.QtyInKg,TC_OrderItems.QtyInBox,TC_OrderItems.Amount,T_Orders.OrderAmount,T_Orders.CreatedOn,TC_OrderItems.Item_id ItemID,s.id SupplierID,c.id CustomerID  
                FROM T_Orders 
                left join TC_InvoicesReferences on TC_InvoicesReferences.Order_id=T_Orders.id and TC_InvoicesReferences.Order_id is null
                join TC_OrderItems on T_Orders.id=TC_OrderItems.Order_id 
                join M_Items on M_Items.id=TC_OrderItems.Item_id                             
                join M_Parties s on T_Orders.Supplier_id=s.id 
                join M_Parties c on T_Orders.Customer_id=c.id 
                left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1
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
                        CustomPrint(OrderQueryresults)
                        
                elif Party != "":
                        # OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,pricelist,Party])
                        OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,Party])
                        
                elif Employee >0:
                        # CustomPrint("Shruti")
                        # OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,pricelist, PartyIDs])
                        OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,PartyIDs])
                        # CustomPrint(OrderQueryresults)
                    
                else:
                        # OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate,pricelist])  
                        OrderQueryresults = T_Orders.objects.raw(OrderQuery, [FromDate,ToDate])   
                # CustomPrint(OrderQueryresults.query)
                if OrderQuery:
                    OrderItemDetails = list()
                    for row in OrderQueryresults:
                        OrderItemDetails.append({
                            "id": row.id,
                            "OrderNo": row.OrderNo,
                            "OrderDate": row.OrderDate,
                            "SupplierName": row.SupplierName,
                            "CustomerName": row.CustomerName,                            
                            "Product": row.GroupName,
                            "SubProduct": row.SubGroup,
                            "SKUName": row.MaterialName,
                            "QtyInNo": float(row.QtyInNo),
                            "QtyInKg": float(row.QtyInKg),
                            "QtyInBox": float(row.QtyInBox),
                            "OrderAmount": float(row.OrderAmount),
                            "CreatedOn": row.CreatedOn  ,
                            "ItemID" :row.ItemID,
                            "SupplierID" :row.SupplierID,  
                            "CustomerID":row.CustomerID                      
                        })
                    log_entry = create_transaction_logNew(request, Orderdata, x, 'From:'+FromDate+','+'To:'+ToDate,31,0,FromDate,ToDate,0)            
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemDetails})
                log_entry = create_transaction_logNew(request, Orderdata, x, "Order Summary Not available",31,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0,'OrderSummaryReport:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


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
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
