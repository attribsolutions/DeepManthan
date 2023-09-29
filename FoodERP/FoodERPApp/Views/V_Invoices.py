from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db.models import Sum
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Invoices import *
from ..Serializer.S_Orders import *
from ..Serializer.S_BankMaster import * 
from ..models import  *


class OrderDetailsForInvoice(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
               
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                Party = Orderdata['Party']
                Customer = Orderdata['Customer']
                POOrderIDs = Orderdata['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderItemDetails = list()
                Orderdata = list()
               

                if POOrderIDs != '':
                    OrderQuery=T_Orders.objects.raw("SELECT T_Orders.Supplier_id id,M_Parties.Name SupplierName,sum(T_Orders.OrderAmount) OrderAmount ,T_Orders.Customer_id CustomerID FROM T_Orders join M_Parties on M_Parties.id=T_Orders.Supplier_id where T_Orders.id IN %s group by T_Orders.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True).data
                    OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                else:
                    query = T_Orders.objects.filter(OrderDate=FromDate,Supplier=Party,Customer=Customer)
                    Serializedata = OrderserializerforInvoice(query,many=True).data
                    Order_list = list()
                    for x in Serializedata:
                        Order_list.append(x['id'])
                        
                    OrderQuery=T_Orders.objects.raw("SELECT T_Orders.Supplier_id id,M_Parties.Name SupplierName,sum(T_Orders.OrderAmount) OrderAmount ,T_Orders.Customer_id CustomerID FROM T_Orders join M_Parties on M_Parties.id=T_Orders.Supplier_id where T_Orders.id IN %s group by T_Orders.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True)
                    OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                       
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemSerializedata})
                for b in OrderItemSerializedata:
                    
                    Item= b['Item']['id']
                    obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,BaseUnitQuantity__gt=0,IsDamagePieces=0)
                    # print(obatchwisestockquery.query)     
                    
                    if obatchwisestockquery == "":
                        StockQtySerialize_data =[]
                    else:   
                        StockQtySerialize_data = StockQtyserializerForInvoice(obatchwisestockquery, many=True).data
                        
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':StockQtySerialize_data})
    
                        stockDatalist = list()
                        for d in StockQtySerialize_data:
                            Rate=RateCalculationFunction(d['LiveBatche']['id'],d['Item']['id'],Customer,0,d['Unit']["UnitID"]["id"],0,0).RateWithGST()
                           
                            if(d['LiveBatche']['MRP']['id'] is None):
                                MRPValue=d['LiveBatche']['MRPValue']
                            else:
                                MRPValue=d['LiveBatche']['MRP']['MRP']
                            
                            if(d['LiveBatche']['GST']['id'] is None):
                                GSTPercentage=d['LiveBatche']['GSTPercentage']
                            else:
                                GSTPercentage=d['LiveBatche']['GST']['GSTPercentage']
                            
                            stockDatalist.append({
                                "id": d['id'],
                                "Item":d['Item']['id'],
                                "BatchDate":d['LiveBatche']['BatchDate'],
                                "BatchCode":d['LiveBatche']['BatchCode'],
                                "SystemBatchDate":d['LiveBatche']['SystemBatchDate'],
                                "SystemBatchCode":d['LiveBatche']['SystemBatchCode'],
                                "LiveBatche" : d['LiveBatche']['id'],
                                "LiveBatcheMRPID" : d['LiveBatche']['MRP']['id'],
                                "LiveBatcheGSTID" : d['LiveBatche']['GST']['id'],
                                "Rate":Rate[0]["NoRatewithOutGST"],
                                "MRP" : MRPValue,
                                "GST" : GSTPercentage,
                                "UnitName":d['Unit']['BaseUnitConversion'], 
                                "BaseUnitQuantity":d['BaseUnitQuantity'],
                                  
                                })
                    # query = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                    # # print(query.query)
                    # if query.exists():
                    #     Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                    #     UnitDetails = list()
                    #     for c in Unitdata:
                           
                    #         UnitDetails.append({
                    #         "Unit": c['id'],
                    #         "UnitName": c['BaseUnitConversion'],
                    #         "ConversionUnit": c['BaseUnitQuantity'],
                    #         "Unitlabel": c['UnitID']['Name'],
                            
                    #     })
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':Unitdata})
                    # =====================Current Discount================================================
                    TodaysDiscount = DiscountMaster(
                        b['Item']['id'], Party, date.today(),Customer).GetTodaysDateDiscount()

                    DiscountType = TodaysDiscount[0]['DiscountType']
                    Discount = TodaysDiscount[0]['TodaysDiscount']

                    OrderItemDetails.append({
                         
                        "id": b['id'],
                        "Item": b['Item']['id'],
                        "ItemName": b['Item']['Name'],
                        "Quantity": b['Quantity'],
                        "MRP": b['MRP']['id'],
                        "MRPValue": b['MRPValue'],
                        "Rate": b['Rate'],
                        "Unit": b['Unit']['id'],
                        "UnitName": b['Unit']['BaseUnitConversion'],
                        "DeletedMCUnitsUnitID": b['Unit']['UnitID']['id'],
                        "ConversionUnit": b['Unit']['BaseUnitQuantity'],
                        "BaseUnitQuantity": b['BaseUnitQuantity'],
                        "GST": b['GST']['id'],
                        "HSNCode": b['GST']['HSNCode'],
                        "GSTPercentage": b['GSTPercentage'],
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
                        "DiscountType" : DiscountType,
                        "Discount" : Discount,
                        "UnitDetails":UnitDropdown(b['Item']['id'],Customer,0),
                        "StockDetails":stockDatalist
                    })
                Orderdata.append({
                    "OrderIDs":Order_list,
                    "OrderItemDetails":OrderItemDetails
                   })  
            log_entry = create_transaction_logNew(request, Orderdata, Party,'Supplier:'+str(Customer),32,0,0,0,Customer)         
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Orderdata[0]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

class InvoiceListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication


    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                FromDate = Invoicedata['FromDate']
                ToDate = Invoicedata['ToDate']
                Customer = Invoicedata['Customer']
                Party = Invoicedata['Party']
               
                if(Customer == ''):
                    query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Party=Party).order_by('-InvoiceDate')
                else:
                    query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Party).order_by('-InvoiceDate')

                # for log
                if(Customer == ''):
                    x = 0
                else:
                    x = Customer
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    Invoice_serializer = InvoiceSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Invoice_serializer})
                    InvoiceListData = list()
                    for a in Invoice_serializer:
                        Count = TC_LoadingSheetDetails.objects.filter(Invoice=a['id']).count()
                        if Count == 0:
                            LoadingSheetCreated = False 
                        else:
                            LoadingSheetCreated = True
                        query2 = MC_PartySubParty.objects.filter(Party=a['Party']['id'],SubParty=a['Customer']['id']).values('IsTCSParty')     
                        InvoiceListData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'],
                            "LoadingSheetCreated": LoadingSheetCreated, 
                            "DriverName": a['Driver']['Name'],
                            "VehicleNo": a['Vehicle']['VehicleNumber'],
                            "Party": a['Party']['Name'],
                            "CreatedOn": a['CreatedOn'],
                            "InvoiceUploads" : a["InvoiceUploads"],
                            "CustomerPartyType":a['Customer']['PartyType_id'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "CustomerPAN": a['Customer']['PAN'],
                            "IsTCSParty":  query2[0]['IsTCSParty']
                        })
                    log_entry = create_transaction_logNew(request, Invoicedata, Party, 'From:'+FromDate+','+'To:'+ToDate,35,0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                log_entry = create_transaction_logNew(request, Invoicedata, Party, "Invoice List Not Found",35,0,FromDate,ToDate,x)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Invoicedata, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class InvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                Party = Invoicedata['Party']
                InvoiceDate = Invoicedata['InvoiceDate']
             
                # ==========================Get Max Invoice Number=====================================================
                a = GetMaxNumber.GetInvoiceNumber(Party,InvoiceDate)
                Invoicedata['InvoiceNumber'] = a
                b = GetPrifix.GetInvoicePrifix(Party)
                Invoicedata['FullInvoiceNumber'] = b+""+str(a)
                #================================================================================================== 
                InvoiceItems = Invoicedata['InvoiceItems']
                O_BatchWiseLiveStockList=list()
                for InvoiceItem in InvoiceItems:
                    # print(InvoiceItem['Quantity'])
                    BaseUnitQuantity=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    InvoiceItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                    QtyInNo=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,1,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInNo'] =  float(QtyInNo)
                    QtyInKg=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,2,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInKg'] =  float(QtyInKg)
                    QtyInBox=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,4,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInBox'] = float(QtyInBox)
                    
                    O_BatchWiseLiveStockList.append({
                        "Quantity" : InvoiceItem['BatchID'],
                        "Item" : InvoiceItem['Item'],
                        "BaseUnitQuantity" : InvoiceItem['BaseUnitQuantity']
                    })
                Invoicedata.update({"obatchwiseStock":O_BatchWiseLiveStockList}) 
                Invoice_serializer = InvoiceSerializer(data=Invoicedata)
                if Invoice_serializer.is_valid():
                    Invoice = Invoice_serializer.save()
                    LastInsertId = Invoice.id
                    log_entry = create_transaction_logNew(request, Invoicedata, Invoicedata['Customer'],'InvoiceDate:'+Invoicedata['InvoiceDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastInsertId),4,LastInsertId,0,0,Party)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully','TransactionID':LastInsertId, 'Data':[]})
                log_entry = create_transaction_logNew(request, Invoicedata, Party, Invoice_serializer.errors,34,0,InvoiceDate,0,Invoicedata['Customer'])
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Invoicedata, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})
    
class InvoiceViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                InvoiceQuery = T_Invoices.objects.filter(id=id)
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceData = list()
                    for a in InvoiceSerializedata:
            
                        InvoiceItemDetails = list()
                        for b in a['InvoiceItems']:
                            aaaa=UnitwiseQuantityConversion(b['Item']['id'],b['Quantity'],b['Unit']['id'],0,0,0,0).GetConvertingBaseUnitQtyBaseUnitName()
                            if (aaaa == b['Unit']['UnitID']['Name']):
                                bb=""
                            else:
                                bb=aaaa   
                                
                            InvoiceItemDetails.append({
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRPValue'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "PrimaryUnitName":b['Unit']['UnitID']['Name'],
                                "UnitName":bb,
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GSTPercentage'],
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
                                "BatchCode": b['BatchCode'],
                                "BatchDate": b['BatchDate'],
                                "HSNCode":b['GST']['HSNCode'],
                                "DiscountType":b['DiscountType'],
                                "Discount":b['Discount'],
                                "DiscountAmount":b['DiscountAmount']
                            })
                            
                            InvoiceReferenceDetails = list()
                            for d in a['InvoicesReferences']:
                                
                                
                                InvoiceReferenceDetails.append({
                                    # "Invoice": d['Invoice'],
                                    "Order": d['Order']['id'],
                                    "FullOrderNumber": d['Order']['FullOrderNumber'],
                                    "Description":d['Order']['Description']
                                })
                            
                        DefCustomerAddress = ''  
                        for ad in a['Customer']['PartyAddress']:
                            if ad['IsDefault'] == True :
                                DefCustomerAddress = ad['Address']
                                
                        DefPartyAddress = ''
                        for x in a['Party']['PartyAddress']:
                            if x['IsDefault'] == True :
                                DefPartyAddress = x['Address']
                                DefPartyFSSAI = x['FSSAINo']

                        # code by ankita 
                        # DefCustomerRoute = ''
                        # for bb in a['Customer']['MCSubParty']:
                        #     # if bb['IsDefault'] == True:
                        #         DefCustomerRoute = bb['Route']['Name']
                        
                        
                        query= MC_PartyBanks.objects.filter(Party=a['Party']['id'],IsSelfDepositoryBank=1,IsDefault=1).all()
                        BanksSerializer=PartyBanksSerializer(query, many=True).data
                        BankData=list()
                        for e in BanksSerializer:
                            if e['IsDefault'] == 1:
                                BankData.append({
                                    "BankName": e['BankName'],
                                    "BranchName": e['BranchName'],
                                    "IFSC": e['IFSC'],
                                    "AccountNo": e['AccountNo'],
                                    "IsDefault" : e['IsDefault']
                                })
                            
                        InvoiceData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "InvoiceNumber": a['InvoiceNumber'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "TCSAmount" : a["TCSAmount"], 
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "CustomerMobileNo": a['Customer']['MobileNo'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "PartyMobileNo": a['Party']['MobileNo'],
                            "PartyFSSAINo": DefPartyFSSAI,
                            "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
                            "PartyState": a['Party']['State']['Name'],
                            "CustomerState": a['Customer']['State']['Name'],
                            "PartyAddress": DefPartyAddress,                            
                            "CustomerAddress": DefCustomerAddress,
                            # "CustomerRoute":DefCustomerRoute,
                            "DriverName":a['Driver']['Name'],
                            "VehicleNo": a['Vehicle']['VehicleNumber'],
                            "CreatedOn" : a['CreatedOn'],
                            "InvoiceItems": InvoiceItemDetails,
                            "InvoicesReferences": InvoiceReferenceDetails,
                            "InvoiceUploads" : a["InvoiceUploads"],
                            "BankData":BankData
                                                        
                        })
                    log_entry = create_transaction_logNew(request, {'InvoiceID':id}, a['Party']['id'], "Single Invoice",50,0,0,0,a['Customer']['id'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
                log_entry = create_transaction_logNew(request, {'InvoiceID':id}, a['Party']['id'], "Invoice Not available",50,0,0,0,a['Customer']['id'])
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Invoice Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata=T_Invoices.objects.all().filter(id=id)
                Invoicedataserializer=InvoiceSerializerForDelete(Invoicedata,many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Delete Successfully', 'Data':Invoicedataserializer})
                
                for a in Invoicedataserializer[0]['InvoiceItems']:
                    BaseUnitQuantity11=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    # print(a['LiveBatch'])
                    if a['LiveBatch'] is None:
                        pass
                    else:
                        selectQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).values('BaseUnitQuantity')
                        UpdateQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).update(BaseUnitQuantity = int(selectQuery[0]['BaseUnitQuantity'] )+int(BaseUnitQuantity11))
                
                row1 = T_Invoices.objects.filter(id=id).values('id','InvoiceDate','InvoiceNumber','FullInvoiceNumber','GrandTotal','RoundOffAmount','CreatedBy','CreatedOn','UpdatedBy','UpdatedOn','Customer','Driver','Party','Vehicle','TCSAmount','Hide')
                new_row1 = T_DeletedInvoices(Invoice=row1[0]['id'],InvoiceDate=row1[0]['InvoiceDate'],InvoiceNumber=row1[0]['InvoiceNumber'],FullInvoiceNumber=row1[0]['FullInvoiceNumber'],GrandTotal=row1[0]['GrandTotal'],RoundOffAmount=row1[0]['RoundOffAmount'],CreatedBy=row1[0]['CreatedBy'],CreatedOn=row1[0]['CreatedOn'],UpdatedBy=row1[0]['UpdatedBy'],UpdatedOn=row1[0]['UpdatedOn'],Customer=row1[0]['Customer'],Driver=row1[0]['Driver'],Party=row1[0]['Party'],Vehicle=row1[0]['Vehicle'],TCSAmount=row1[0]['TCSAmount'],Hide=row1[0]['Hide'])
                new_row1.save() 
                
                rows_to_move = TC_InvoiceItems.objects.filter(Invoice=id).values('BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch','MRPValue','GSTPercentage','QtyInBox','QtyInKg','QtyInNo','Invoice')
                # Create a list of instances for Table2 using data from Table1
                new_rows = [TC_DeletedInvoiceItems(Quantity=row['Quantity'], BaseUnitQuantity=row['BaseUnitQuantity'], MRPValue=row['MRPValue'],Rate =row['Rate'],BasicAmount=row['BasicAmount'],TaxType=row['TaxType'],GSTPercentage=row['GSTPercentage'],GSTAmount=row['GSTAmount'],Amount=row['Amount'],DiscountType=row['DiscountType'],Discount=row['Discount'],DiscountAmount=row['DiscountAmount'],CGST=row['CGST'],SGST=row['SGST'],IGST=row['IGST'],CGSTPercentage=row['CGSTPercentage'],SGSTPercentage=row['SGSTPercentage'],IGSTPercentage=row['IGSTPercentage'],BatchDate=row['BatchDate'],BatchCode=row['BatchCode'],CreatedOn=row['CreatedOn'],GST=row['GST'],Invoice=row['Invoice'],Item=row['Item'],LiveBatch=row['LiveBatch'],MRP=row['MRP'],Unit=row['Unit'],QtyInNo=row['QtyInNo'],QtyInKg=row['QtyInKg'],QtyInBox=row['QtyInBox']) for row in rows_to_move]
                # Bulk insert the new rows into Table2
                aaa=TC_DeletedInvoiceItems.objects.bulk_create(new_rows)
                
                row2 = TC_InvoiceUploads.objects.filter(Invoice=id).values('Irn', 'EInvoicePdf', 'QRCodeUrl', 'AckNo', 'EwayBillUrl', 'EInvoiceCreatedBy', 'EInvoiceCanceledBy', 'EInvoiceIsCancel', 'Invoice', 'EwayBillNo', 'EInvoiceCanceledOn', 'EInvoiceCreatedOn', 'EwayBillCanceledBy', 'EwayBillCanceledOn', 'EwayBillCreatedBy', 'EwayBillCreatedOn', 'EwayBillIsCancel', 'user_gstin')
                if row2:
                    new_row2 = TC_DeletedInvoiceUploads(Irn=row2[0]['Irn'],EInvoicePdf=row2[0]['EInvoicePdf'],QRCodeUrl=row2[0]['QRCodeUrl'],AckNo=row2[0]['AckNo'],EwayBillUrl=row2[0]['EwayBillUrl'],EInvoiceCreatedBy=row2[0]['EInvoiceCreatedBy'],EInvoiceCanceledBy=row2[0]['EInvoiceCanceledBy'],EInvoiceIsCancel=row2[0]['EInvoiceIsCancel'],Invoice=row2[0]['Invoice'],EwayBillNo=row2[0]['EwayBillNo'],EInvoiceCanceledOn=row2[0]['EInvoiceCanceledOn'],EInvoiceCreatedOn=row2[0]['EInvoiceCreatedOn'],EwayBillCanceledBy=row2[0]['EwayBillCanceledBy'],EwayBillCanceledOn=row2[0]['EwayBillCanceledOn'],EwayBillCreatedBy=row2[0]['EwayBillCreatedBy'],EwayBillCreatedOn=row2[0]['EwayBillCreatedOn'],EwayBillIsCancel=row2[0]['EwayBillIsCancel'],user_gstin=row2[0]['user_gstin'])
                    new_row2.save()
                else:  
                    pass
                 
                row3 = TC_InvoicesReferences.objects.filter(Invoice=id).values('Invoice','Order')
               
                if row3.exists(): 
                    new_row3 = TC_DeletedInvoicesReferences(Invoice=row3[0]['Invoice'],Order=row3[0]['Order'])
                    new_row3.save()
                else:
                    pass                                                                                                                                                                                                                                                               
                
                Invoicedata = T_Invoices.objects.get(id=id)
                Invoicedata.delete()
                log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0, '',6,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Delete Successfully', 'Data':[]})
        except IntegrityError:
            log_entry = create_transaction_logNew(request,  {'InvoiceID':id}, 0, '',8,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,  {'InvoiceID':id}, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 
          
class InvoiceNoView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    @transaction.atomic()

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                InVoice_Data = JSONParser().parse(request)  
                Party = InVoice_Data['PartyID']
                Customer = InVoice_Data['CustomerID']

                if Party == '':
                    x = Customer
                else:
                    x = Party

                query = T_Invoices.objects.filter(Party=Party,Customer=Customer)
                if query.exists:
                    Invoice_Serializer = InvoiceSerializerSecond(query,many=True).data
                    InvoiceList = list()
                    for a in Invoice_Serializer:
                        InvoiceList.append({
                            "Invoice":a['id'],
                            "FullInvoiceNumber":a['FullInvoiceNumber'],
                        })
                    log_entry = create_transaction_logNew(request, InVoice_Data, x,'InvoiceNoList',36,0,0,0,Customer)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceList})
                log_entry = create_transaction_logNew(request, InVoice_Data, x, "Invoice No List Not Found",36,0,0,0,Customer)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, InVoice_Data, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 

##################### Purchase Return Invoice View ###########################################     
        
class InvoiceViewThird(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                InvoiceQuery = T_Invoices.objects.filter(id=id)
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(
                        InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceData = list()
                    for a in InvoiceSerializedata:
                        InvoiceItemDetails = list()
                        for b in a['InvoiceItems']:
                            ChildItem= b['Item']['id']
                            Unitquery = MC_ItemUnits.objects.filter(Item_id=ChildItem,IsDeleted=0)
                            # print(query.query)
                            if Unitquery.exists():
                                Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                                ItemUnitDetails = list()
                               
                                for c in Unitdata:
                                    ItemUnitDetails.append({
                                    "Unit": c['id'],
                                    "UnitName": c['BaseUnitConversion'],
                                })
                                    
                            MRPquery = M_MRPMaster.objects.filter(Item_id=ChildItem).order_by('-id')[:3] 
                            # print(query.query)
                            if MRPquery.exists():
                                MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                                ItemMRPDetails = list()
                               
                                for d in MRPdata:
                                    ItemMRPDetails.append({
                                    "MRP": d['id'],
                                    "MRPValue": d['MRP'],   
                                })
                                    
                            GSTquery = M_GSTHSNCode.objects.filter(Item_id=ChildItem).order_by('-id')[:3] 
                            # print(query.query)
                            if GSTquery.exists():
                                Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                                ItemGSTDetails = list()
                                
                                for e in Gstdata:
                                    ItemGSTDetails.append({
                                    "GST": e['id'],
                                    "GSTPercentage": e['GSTPercentage'],   
                                })                
                                    
                            InvoiceItemDetails.append({
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRPValue'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GSTPercentage'],
                                "BasicAmount": b['BasicAmount'],
                                "GSTAmount": b['GSTAmount'],
                                "CGST": b['CGST'],
                                "SGST": b['SGST'],
                                "IGST": b['IGST'],
                                "CGSTPercentage": b['CGSTPercentage'],
                                "SGSTPercentage": b['SGSTPercentage'],
                                "IGSTPercentage": b['IGSTPercentage'],
                                "Amount": b['Amount'],
                                "BatchCode": b['BatchCode'],
                                "BatchDate": b['BatchDate'],
                                "DiscountType": b['DiscountType'],
                                "Discount": b['Discount'],
                                "DiscountAmount": b['DiscountAmount'],
                                "ItemUnitDetails":ItemUnitDetails,
                                "ItemMRPDetails":ItemMRPDetails,
                                "ItemGSTDetails":ItemGSTDetails,
                                
                            })
                            
                        InvoiceData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "InvoiceNumber": a['InvoiceNumber'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "CreatedOn" : a['CreatedOn'],
                            "InvoiceItems": InvoiceItemDetails,
                                               
                        })
                    log_entry = create_transaction_logNew(request, {'InvoiceID':id}, a['Party']['id'],'InvoiceData',64,0,0,0,a['Customer']['id'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
                log_entry = create_transaction_logNew(request, {'InvoiceID':id}, a['Party']['id'], "Order Data Not available",64,0,0,0,a['Customer']['id'])
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})                                      
 
class BulkInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                for aa in Invoicedata['BulkData']:
                    CustomerMapping=M_PartyCustomerMappingMaster.objects.filter(MapCustomer=aa['Customer'],Party=aa['Party']).values("Customer")
                   
                    if CustomerMapping.count() > 0:
                        aa['Customer']=CustomerMapping[0]['Customer']
                    else:
                        # log_entry = create_transaction_logNew(request, Invoicedata, 0, "Customer Data Mapping Missing",37,0)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Customer Data Mapping Missing", 'Data':[]})    
                    # print(aa['Customer'])
                    for bb in aa['InvoiceItems']:
                        ItemMapping=M_ItemMappingMaster.objects.filter(MapItem=bb['Item'],Party=aa['Party']).values("Item")
                        if ItemMapping.count() > 0:
                            bb['Item']=ItemMapping[0]['Item']
                        else:
                            # log_entry = create_transaction_logNew(request, Invoicedata, 0, "Item Data Mapping Missing",38,0)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Item Data Mapping Missing", 'Data':[]})     
                        UnitMapping=M_UnitMappingMaster.objects.filter(MapUnit=bb['Unit'],Party=aa['Party']).values("Unit")
                        if UnitMapping.count() > 0:
                            MC_UnitID=MC_ItemUnits.objects.filter(UnitID=UnitMapping[0]["Unit"],Item=ItemMapping[0]["Item"],IsDeleted=0).values("id")
                            if MC_UnitID.count() > 0:
                                bb['Unit']=MC_UnitID[0]['id']
                            else:
                                # log_entry = create_transaction_logNew(request, Invoicedata, 0, " MC_ItemUnits Data Mapping Missing",39,0)
                                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " MC_ItemUnits Data Mapping Missing", 'Data':[]})            
                        else:
                            # log_entry = create_transaction_logNew(request, Invoicedata, 0, "Unit Data Mapping Missing",40,0)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Unit Data Mapping Missing", 'Data':[]})
                    Invoice_serializer = BulkInvoiceSerializer(data=aa)
                    if Invoice_serializer.is_valid():
                        Invoice_serializer.save()
                    else:
                        transaction.set_rollback(True)
                        # log_entry = create_transaction_logNew(request, Invoicedata, 0, Invoice_serializer.errors,34,0)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data': []})
                # log_entry = create_transaction_logNew(request, Invoicedata, 0, 'Invoice Save Successfully',4,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully', 'Data':[]})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, Invoicedata, 0, e, 33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})
        


class InvoiceHideView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def delete(self, request, id=0,Mode=0):
        try:
            with transaction.atomic():
                if Mode == '0':
                    InvoiceUpdate = T_Invoices.objects.filter(id=id).update(Hide=0) 
                    log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0,'',65,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Un-Hide Successfully ', 'Data':[]})
                else:
                    InvoiceUpdate = T_Invoices.objects.filter(id=id).update(Hide=1)
                    log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0,'',66,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Hide Successfully ', 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]}) 
        
        
class UpdateVehicleInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0,vehicle=0):
        try:
            with transaction.atomic():
                VehicleUpdate = T_Invoices.objects.filter(id=id).update(Vehicle=vehicle)
                log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0,'',67,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': ' Vehicle No Updated Against Invoice Successfully ', 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, {'InvoiceID':id}, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})    
        


  

class InvoiceViewEditView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                
                query1 = TC_InvoicesReferences.objects.filter(Invoice=id).values('Order')
                Orderdata = list()
                query = T_Invoices.objects.filter(id=id).values('Customer','InvoiceNumber','FullInvoiceNumber')
                # print(query.query)
                Customer=query[0]['Customer']
                InvoiceNumber=query[0]['InvoiceNumber']
                FullInvoiceNumber=query[0]['FullInvoiceNumber']
                Itemsquery= TC_InvoiceItems.objects.raw('''SELECT TC_InvoiceItems.id,TC_InvoiceItems.Item_id,M_Items.Name ItemName,TC_InvoiceItems.Quantity,TC_InvoiceItems.MRP_id,TC_InvoiceItems.MRPValue,TC_InvoiceItems.Rate,TC_InvoiceItems.Unit_id,MC_ItemUnits.BaseUnitConversion UnitName,MC_ItemUnits.UnitID_id DeletedMCUnitsUnitID,MC_ItemUnits.BaseUnitQuantity ConversionUnit,TC_InvoiceItems.BaseUnitQuantity,TC_InvoiceItems.GST_id,M_GSTHSNCode.HSNCode,TC_InvoiceItems.GSTPercentage,TC_InvoiceItems.BasicAmount,TC_InvoiceItems.GSTAmount,CGST, SGST, IGST, CGSTPercentage,SGSTPercentage, IGSTPercentage,Amount,DiscountType,Discount,DiscountAmount FROM TC_InvoiceItems JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id JOIN MC_ItemUnits ON MC_ItemUnits.id = TC_InvoiceItems.Unit_id JOIN M_GSTHSNCode ON M_GSTHSNCode.id = TC_InvoiceItems.GST_id Where TC_InvoiceItems.Invoice_id=%s ''',([id]))
                if Itemsquery:
                    InvoiceEditSerializer = InvoiceEditItemSerializer(Itemsquery, many=True).data
                    OrderItemDetails=list()
                    seen_item_ids = set()
                    for b in InvoiceEditSerializer:
                        item_id = b['Item_id']
                      
                        if item_id in seen_item_ids:
                            break  # Exit the loop when a repeated Item_id is encountered
                        seen_item_ids.add(item_id)  # Add the current Item_id to the set of seen Item_ids
                        batchquery = TC_InvoiceItems.objects.filter(Item=item_id,Invoice = id).values('LiveBatch_id')
                        LiveBatchIDlist = list(batchquery.values_list('LiveBatch_id', flat=True))
                        # print(LiveBatchIDlist)
                        stockquery=O_LiveBatches.objects.raw('''SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,O_LiveBatches.BatchDate,O_LiveBatches.BatchCode,O_LiveBatches.SystemBatchDate,O_LiveBatches.SystemBatchCode,O_LiveBatches.id As LiveBatchID,TC_InvoiceItems.MRP_id,TC_InvoiceItems.GST_id,TC_InvoiceItems.MRPValue,TC_InvoiceItems.GSTPercentage,MC_ItemUnits.UnitID_id,MC_ItemUnits.BaseUnitConversion,TC_InvoiceItems.BaseUnitQuantity FROM O_LiveBatches JOIN O_BatchWiseLiveStock ON O_BatchWiseLiveStock.LiveBatche_id =O_LiveBatches.id JOIN MC_ItemUnits ON MC_ItemUnits.id = O_BatchWiseLiveStock.Unit_id JOIN TC_InvoiceItems ON TC_InvoiceItems.LiveBatch_id = O_LiveBatches.id WHERE  TC_InvoiceItems.Invoice_id=%s AND O_BatchWiseLiveStock.LiveBatche_id IN %s  ''',(id,LiveBatchIDlist))
                
                        InvocieEditStock=InvoiceEditStockSerializer(stockquery,many=True).data
                        stockDatalist = list()
                        queryset = TC_InvoiceItems.objects.filter(Item_id=item_id,Invoice_id=id,LiveBatch_id__in=LiveBatchIDlist).aggregate(Quantity=Sum('Quantity'))
                        quantity_sum = queryset.get('Quantity', 0)
                       
                       

                        for d in InvocieEditStock:
                            Rate=RateCalculationFunction(d['LiveBatchID'],d['Item_id'],Customer,0,d["UnitID_id"],0,0).RateWithGST()

                            stockDatalist.append({
                                    "id": d['id'],
                                    "Item":d['Item_id'],
                                    "BatchDate":d['BatchDate'],
                                    "BatchCode":d['BatchCode'],
                                    "SystemBatchDate":d['SystemBatchDate'],
                                    "SystemBatchCode":d['SystemBatchCode'],
                                    "LiveBatche" : d['LiveBatchID'],
                                    "LiveBatcheMRPID" : d['MRP_id'],
                                    "LiveBatcheGSTID" : d['GST_id'],
                                    "Rate":Rate[0]["NoRatewithOutGST"],
                                    "MRP" : d['MRPValue'],
                                    "GST" : d['GSTPercentage'],
                                    "UnitName":d['BaseUnitConversion'], 
                                    "BaseUnitQuantity":d['BaseUnitQuantity'],
                                    
                                    })
                        
                            OrderItemDetails.append({
                                
                                "id": b['id'],
                                "Item": item_id,
                                "ItemName": b['ItemName'],
                                "Quantity": quantity_sum,
                                "MRP": b['MRP_id'],
                                "MRPValue": b['MRPValue'],
                                "Rate": b['Rate'],
                                "Unit": b['Unit_id'],
                                "UnitName": b['UnitName'],
                                "DeletedMCUnitsUnitID":b['DeletedMCUnitsUnitID'],
                                "ConversionUnit": b['ConversionUnit'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST_id'],
                                "HSNCode": b['HSNCode'],
                                "GSTPercentage": b['GSTPercentage'],
                                "BasicAmount": b['BasicAmount'],
                                "GSTAmount": b['GSTAmount'],
                                "CGST": b['CGST'],
                                "SGST": b['SGST'],
                                "IGST": b['IGST'],
                                "CGSTPercentage": b['CGSTPercentage'],
                                "SGSTPercentage": b['SGSTPercentage'],
                                "IGSTPercentage": b['IGSTPercentage'],
                                "Amount": b['Amount'],
                                "DiscountType" : b['DiscountType'],
                                "Discount" :b['Discount'] ,
                                "DiscountAmount":b['DiscountAmount'],
                                "UnitDetails":UnitDropdown(b['Item_id'],Customer,0),
                                "StockDetails":stockDatalist
                            })
                    Orderdata.append({
                        "OrderIDs":[str(query1[0]['Order'])],
                        "OrderItemDetails":OrderItemDetails,
                        "InvoiceNumber":InvoiceNumber,
                        "FullInvoiceNumber":FullInvoiceNumber
                        })       
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Orderdata[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})  
    
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                
                Invoicedata = JSONParser().parse(request)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Bomsdata })
                InvoicedataByID = T_Invoices.objects.get(id=id)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(BomsdataByID.query)})
                InvoiceItems = Invoicedata['InvoiceItems']
                O_BatchWiseLiveStockList=list()
                for InvoiceItem in InvoiceItems:
                    # print(InvoiceItem['Quantity'])
                    BaseUnitQuantity=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    InvoiceItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                    QtyInNo=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,1,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInNo'] =  float(QtyInNo)
                    QtyInKg=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,2,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInKg'] =  float(QtyInKg)
                    QtyInBox=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,4,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInBox'] = float(QtyInBox)
                    
                    O_BatchWiseLiveStockList.append({
                        "id" : InvoiceItem['BatchID'],
                        "LiveBatche":InvoiceItem['LiveBatch'],
                        "Item" : InvoiceItem['Item'],
                        "BaseUnitQuantity" : InvoiceItem['BaseUnitQuantity'],
                        "PreviousInvoiceBaseUnitQuantity" : InvoiceItem['PreviousInvoiceBaseUnitQuantity']
                    })
                Invoicedata.update({"obatchwiseStock":O_BatchWiseLiveStockList})
                Invoice_Serializer = UpdateInvoiceSerializer(InvoicedataByID, data=Invoicedata)
                
                if Invoice_Serializer.is_valid():
                    Invoice_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Invoice_Serializer.errors, 'Data': []})    
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})     
                                  