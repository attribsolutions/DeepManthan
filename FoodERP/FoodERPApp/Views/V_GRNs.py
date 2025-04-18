
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_GRNs import *
from ..Serializer.S_Orders import *
from ..Serializer.S_Challan import *
from ..Serializer.S_Invoices import *
from ..Serializer.S_Bom import *
from ..models import *
from django.db.models import *
from datetime import datetime, timedelta 
from decimal import Decimal
from rest_framework.views import APIView

# GRN List API

class GRNListFilterView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        GRNdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                FromDate = GRNdata['FromDate']
                ToDate = GRNdata['ToDate']
                Customer = GRNdata['Party']
                Supplier = GRNdata['Supplier']
                IsGRNType=GRNdata['IsGRNType']
                # print('aaaaaaaaaaaaaaaaaaaaa')
                if(Supplier == ''):
                    # print("shruti")
                    # query = T_GRNs.objects.filter(
                    #     GRNDate__range=[FromDate, ToDate], Customer_id=Customer)
                    # print(query.query)
                    condition=""
                    
                else:
                    condition=f'''and G.Party_id = {Supplier}'''
                    # query = T_GRNs.objects.filter(
                    #     GRNDate__range=[FromDate, ToDate], Customer_id=Customer, Party_id=Supplier)
                # print('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')    
                query =T_GRNs.objects.raw(f''' select G.id,  G.GRNDate, G.Customer_id, G.GRNNumber, G.FullGRNNumber,G.InvoiceNumber,G.GrandTotal, G.Party_id, G.CreatedBy, G.UpdatedBy,G.CreatedOn, G.Comment
                                            ,party.Name PartyName,cust.Name customerName,cust.id customerid,T_Invoices.InvoiceNumber,
                                          T_Invoices.InvoiceDate,party.id PartyID,T_Invoices.id InvoiceID,T_Invoices.FullInvoiceNumber, G.IsSave,G.TotalExpenses
                                          from T_GRNs G

join M_Parties party on party.id=G.Party_id
join M_Parties cust on cust.id=G.Customer_id
join TC_GRNReferences on TC_GRNReferences.GRN_id=G.id
left join T_Invoices on T_Invoices.id=TC_GRNReferences.Invoice_id
where GRNDate between %s and %s and G.Customer_id= %s and IsGRNType={IsGRNType} {condition}''',[FromDate,ToDate,Customer])
                
                # print(query)
                if not query:
                    log_entry = create_transaction_logNew(request, GRNdata, Customer,'List Not available',68,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    # GRN_serializer = T_GRNSerializerForGET(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRN_serializer})
                    GRNListData = list()
                    # print(GRN_serializer)
                    for a in query:
                        
                        # print("RRRRRRRRRRRRRRRRRRRRRR",a)
                        if (GRNdata['DashBoardMode'] == 1):
                            GRNListData.append({
                                "GRNDate": a.GRNDate                
                            })
                        else:
                            pass
                            # print("Shrutirriri")
                            # x = a.get('GRNReferences')
                            # # print(a.get('GRNReferences'))                         
                            # # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': a})
                            # challan = None 
                            
                            # if x:
                            #     # print("hhhhhhhhh")
                            #     challan = x[0]['Challan']
                            #     # print(challan)
                            #     POType= ""
                            #     # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': x})
                            # else:
                            POType= ""
                        
                            # challan = a['GRNReferences'][0]['Challan']
                            # if challan != None: 
                            #     POType= ""
                            # else:
                            #     POType= ""
                            #     # POType= a['GRNReferences'][0]['Order']['POType']['id']
                            GRNListData.append({
                                "id": a.id,
                                "GRNDate": a.GRNDate,
                                "Customer": a.customerid,
                                "CustomerName": a.customerName,
                                "GRNNumber": a.GRNNumber,
                                "FullGRNNumber": a.FullGRNNumber,
                                "InvoiceNumber": a.InvoiceNumber,
                                "FullInvoiceNumber":a.FullInvoiceNumber if a.FullInvoiceNumber else a.InvoiceNumber,
                                "InvoiceDate": a.InvoiceDate if a.InvoiceNumber else "",
                                "InvoiceID" : a.InvoiceID,
                                "GrandTotal": a.GrandTotal,
                                "Party": a.PartyID,
                                "PartyName": a.PartyName,
                                "CreatedOn" : a.CreatedOn,
                                "POType":POType,
                                "IsSave" : a.IsSave,
                                "TotalExpenses":a.TotalExpenses

                            })
                    # print(GRNListData)
                    #for log.
                    if Supplier == '':
                        y = 0
                    else:
                        y= Supplier
                    # print("ssssssssssssssssssss")
                    # print(GRNListData)
                    log_entry = create_transaction_logNew(request, GRNdata,Customer,'From:'+FromDate+','+'To:'+ToDate+','+'Supplier:'+str(y),68,0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData})
                
        except Exception as e:
            log_entry = create_transaction_logNew(request, GRNdata, 0,'GRNList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

# GRN Save  API

class T_GRNView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        GRNdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Customer = GRNdata['Customer']
                CreatedBy = GRNdata['CreatedBy']
                GRNDate = GRNdata['GRNDate']
                IsGRNType= GRNdata['IsGRNType']
                # CustomPrint(GRNdata['GRNReferences'])
                # if R in GRNdata['GRNReferences']:
                #     Query =T_Orders.objects.filter(id=OrderID[0]).update(Inward=GRNReference_data['Inward'])
# ==========================Get Max GRN Number=====================================================
                a = GetMaxNumber.GetGrnNumber(Customer,GRNDate)
                GRNdata['GRNNumber'] = a
                if IsGRNType !=0:                    
                    b = GetPrifix.GetGrnPrifix(Customer)
                else:
                    b = GetPrifix.GetIBInwardPrifix(Customer)
                
                b = b.strip() if b else ""
                GRNdata['FullGRNNumber'] = b+""+str(a)
#================================================================================================== 
                item = ""
                query = T_GRNs.objects.filter(Customer_id=GRNdata['Customer']).values('id')
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                for a in GRNdata['GRNItems']:
                  
                    query1 = TC_GRNItems.objects.filter(Item_id=a['Item'], SystemBatchDate=date.today(), GRN_id__in=query).values('id')
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                    DaysofItems = query2[0]['Days'] if query2 else 0
                    batch_date = datetime.strptime(a['BatchDate'], '%Y-%m-%d')                
                    
                    if 'ItemExpiryDate' in a and a['ItemExpiryDate']:
                        ItemExpiryDate = a['ItemExpiryDate'] 
                    else:
                        ItemExpiryDateStr = batch_date + timedelta(days=DaysofItems)
                        ItemExpiryDate = ItemExpiryDateStr.strftime('%Y-%m-%d')  

                    
                    if(item == ""):
                        item = a['Item']
                        b = query1.count()

                    elif(item == a['Item']):
                        item = 1
                        b = b+1
                    else:
                        item = a['Item']
                        b = 0

                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], GRNdata['Customer'], b)
                    
                    BaseUnitQuantity=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    a['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                    QtyInNo=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,1,0).ConvertintoSelectedUnit()
                    a['QtyInNo'] =  float(QtyInNo)
                    QtyInKg=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,2,0).ConvertintoSelectedUnit()
                    a['QtyInKg'] =  float(QtyInKg)
                    QtyInBox=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,4,0).ConvertintoSelectedUnit()
                    a['QtyInBox'] = float(QtyInBox)
                    
                    
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    
                    
                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": round(BaseUnitQuantity,3),
                    "OriginalBaseUnitQuantity": round(BaseUnitQuantity,3),
                    "Party": Customer,
                    "CreatedBy":CreatedBy,
                    
                    })  
                    O_LiveBatchesList.append({
                    "ItemExpiryDate":ItemExpiryDate,
                    "MRP": a['MRP'],
                    "Rate": a['Rate'],
                    "GST": a['GST'],
                    "GSTPercentage":a["GSTPercentage"],
                    "MRPValue":a["MRPValue"],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : round(BaseUnitQuantity,6),
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList                   
                    })
                    O_BatchWiseLiveStockList=list()
                    
                   
                # CustomPrint(GRNdata)
                GRNdata.update({"O_LiveBatchesList":O_LiveBatchesList}) 
                # return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'GRN Save Successfully', 'Data': GRNdata})   
                GRN_serializer = T_GRNSerializer(data=GRNdata)
                if GRN_serializer.is_valid():
                    # return JsonResponse({'Data':GRN_serializer.data})
                    GRN = GRN_serializer.save()
                    LastInsertId = GRN.id
                    log_entry = create_transaction_logNew(request, GRNdata, GRNdata['Party'],'GRNDate:'+GRNdata['GRNDate']+','+'Supplier:'+str(Customer)+','+'TransactionID:'+str(LastInsertId),69,LastInsertId,0,0,Customer)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'GRN Save Successfully', 'TransactionID':LastInsertId, 'Data': []})
                log_entry = create_transaction_logNew(request, GRNdata,0,'GRNSave:'+str(GRN_serializer.errors),34,0)
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': GRN_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, GRNdata, 0,'GRNSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

# UPDATE GRN 

class T_GRNViewUpdate(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, id=0):
        GRNupdatedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GRNupdateByID = T_GRNs.objects.get(id=id)
                print(GRNupdateByID)
                
                for item in GRNupdatedata['GRNItems']:
                    BaseUnitQuantity = UnitwiseQuantityConversion(
                        item['Item'], item['Quantity'], item['Unit'], 0, 0, 0, 0).GetBaseUnitQuantity()
                    item['BaseUnitQuantity'] = BaseUnitQuantity
                    QtyInNo = UnitwiseQuantityConversion(
                        item['Item'], item['Quantity'], item['Unit'], 0, 0, 1, 0).ConvertintoSelectedUnit()
                    item['QtyInNo'] = QtyInNo
                    QtyInKg = UnitwiseQuantityConversion(
                        item['Item'], item['Quantity'], item['Unit'], 0, 0, 2, 0).ConvertintoSelectedUnit()
                    item['QtyInKg'] = QtyInKg
                    QtyInBox = UnitwiseQuantityConversion(
                        item['Item'], item['Quantity'], item['Unit'], 0, 0, 4, 0).ConvertintoSelectedUnit()
                    item['QtyInBox'] = QtyInBox
                
                GRNupdate_Serializer = T_GRNSerializer(GRNupdateByID, data=GRNupdatedata)
                if GRNupdate_Serializer.is_valid():
                    GRNupdate_Serializer.save()  
                # TC_GRNExpenses save
                # TC_GRNExpenses.objects.filter(grn_id=id).delete()

                    # Save new GRNExpenses data
                    total_expense_amount = 0
                    for exp in GRNupdatedata.get('GRNExpenses', []):                        
                        expense = TC_GRNExpenses.objects.create(
                            GRN_id=exp.get('GRN',0),                        
                            Ledger_id=exp.get('Ledger',0),
                            Amount=Decimal(exp.get('Amount', 0) or 0),
                            GSTPercentage=exp.get('GSTPercentage', 0),
                            CGST=exp.get('CGST', 0),
                            SGST=exp.get('SGST', 0),
                            IGST=exp.get('IGST', 0),
                            BasicAmount=exp.get('BasicAmount', 0)
                        )
                        
                        # total_expense_amount += Decimal(expense.Amount or 0)
                    total_expense_amount= GRNupdatedata['TotalExpense']

                        # Update TotalExpenses in T_GRNs
                    GRNupdateByID.TotalExpenses = total_expense_amount
                    GRNupdateByID.save()
                        
                        
                    log_entry = create_transaction_logNew(request, GRNupdatedata, 0,'GRN Updated - ID: ' + str(id), 450, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GRN Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, GRNupdatedata, 0, 'GRNEdit:' + str(GRNupdate_Serializer.errors), 450, 0)
                    transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': False, 'Message': GRNupdate_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, GRNupdatedata, 0, 'GRNEdit:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': Exception(e), 'Data': []})
        
        


#GRN Single Get API

class T_GRNViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                GRNdata = T_GRNs.objects.get(id=id)
                GRN_serializer = T_GRNSerializerForGET(GRNdata).data
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
                        "MRP": a['MRP']['id'],
                        "MRPValue": a['MRPValue'],
                        "ReferenceRate": a['ReferenceRate'],
                        "Rate": a['Rate'],
                        "BasicAmount": a['BasicAmount'],
                        "TaxType": a['TaxType'],
                        "GST": a['GST']['id'],
                        "GSTPercentage": a['GSTPercentage'],
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
                        "DiscrepancyComment" : a['DiscrepancyComment'],
                        "AccountingQuantity" : a['AccountingQuantity'],
                        "ItemExpiryDate" : a['ItemExpiryDate'],
                        "UnitDetails":[]
                    })

                GRNReferencesData = list()
                for r in GRN_serializer['GRNReferences']:
                    GRNReferencesData.append({
                        "Invoice": r['Invoice'],
                        "Order": r['Order'],
                        "ChallanNo": r['ChallanNo'],
                    })
                GRNListData = list()
                a = GRN_serializer
                GRNListData.append({
                    "id": a['id'],
                    "GRNDate": a['GRNDate'],
                    "Customer": a['Customer']['id'],
                    "CustomerName": a['Customer']['Name'],
                    "PriceList_id": a['Customer']['PriceList_id'],
                    "GRNNumber": a['GRNNumber'],
                    "FullGRNNumber": a['FullGRNNumber'],
                    "InvoiceNumber": a['InvoiceNumber'],
                    "GrandTotal": a['GrandTotal'],
                    "Party": a['Party']['id'],
                    "PartyName": a['Party']['Name'],
                    "CreatedBy": a['CreatedBy'],
                    "UpdatedBy": a['UpdatedBy'],
                    "Comment" : a['Comment'],
                    "IsSave" : a['IsSave'],
                    "GRNReferences": GRNReferencesData,
                    "GRNItems": GRNItemListData
                })
                log_entry = create_transaction_logNew(request, {'GRNID':id}, a['Party']['id'],'Single GRN',70,0,0,0,a['Customer']['id'])
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData})
        except Exception as e:
            log_entry = create_transaction_logNew(request,{'GRNID':id}, 0,'SingleGRN:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
 
# GRN DELETE API 
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                O_BatchWiseLiveStockData = O_BatchWiseLiveStock.objects.filter(GRN_id=id).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
              
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'GRN Used in another Transaction', 'Data': []})   
                
                GRN_Data = T_GRNs.objects.get(id=id)
                GRN_Data.delete()
                log_entry = create_transaction_logNew(request, {'GRNID':id}, 0,'GRN Deleted Successfully',71,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GRN Deleted Successfully', 'Data': []})
        except T_GRNs.DoesNotExist:
            log_entry = create_transaction_logNew(request, {'GRNID':id}, 0,'GRN Not Exist',71,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, {'GRNID':id}, 0,'GRN Used in another Transaction',72,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'GRN Used in another Transaction', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GRNDelete:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})    
            
# Get PO Details For Make GRN POST API 

class GetOrderDetailsForGrnView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                POOrderIDs = request.data['OrderIDs']
                Mode = request.data['Mode']
                Order_list = POOrderIDs.split(",")
                OrderData = list()
                OrderItemDetails = list()
                
                # Check if GRN exists for any of the given OrderIDs
                grn_exists = TC_GRNReferences.objects.filter(Order_id__in=Order_list).exists()
              
                IsSave = 2 if grn_exists else 1
               
                if Mode == 1:
                    OrderQuery=T_Orders.objects.raw('''SELECT T_Orders.Supplier_id id,M_Parties.Name SupplierName,sum(T_Orders.OrderAmount) OrderAmount ,T_Orders.Customer_id CustomerID,P.PriceList_id PriceListId
                    FROM T_Orders 
                    join M_Parties on M_Parties.id=T_Orders.Supplier_id 
                    JOIN M_Parties P ON P.id=T_Orders.Customer_id
                    where T_Orders.id IN %s group by T_Orders.Supplier_id''',[Order_list])
                    if not OrderQuery:
                        log_entry = create_transaction_logNew(request, 0, 0,"Records Not Found",29,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                    else:
                        item = ""
                        OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True).data
                        OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                        OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data                       
                        Ordersquery = T_Orders.objects.filter(Customer_id=OrderSerializedata[0]['CustomerID']).values('id')
                            # Convert QuerySet to a list to make it JSON serializable
                            # query_list = list(query)
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': query_list})
                        for b in OrderItemSerializedata:
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': b})
                                Item= b['Item']['id']
                                Batchquery1 = TC_OrderItems.objects.filter(Item_id=Item, Order_id__in=Ordersquery).values('id')
                                if(item == ""):
                                    item = Item
                                    c = Batchquery1.count()

                                elif(item == Item):
                                    item = 1
                                    c = c+1
                                else:
                                    item = Item
                                    c = 0

                                BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(Item, OrderSerializedata[0]['CustomerID'], 0)
                                query = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                                # CustomPrint(query.query)
                                if query.exists():
                                    Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                                    UnitDetails = list()
                                    for c in Unitdata:
                                        if c['IsDeleted']== 0 :
                                            UnitDetails.append({
                                            "Unit": c['id'],
                                            "UnitName": c['BaseUnitConversion'],
                                        })
                                            
                                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':Unitdata})
                                OrderItemDetails.append({
                                    "id": b['id'],
                                    "Item": b['Item']['id'],
                                    "ItemName": b['Item']['Name'],
                                    "Quantity": b['Quantity'],
                                    "MRP": b['MRP']['id'],
                                    "MRPValue": b['MRP']['MRP'],
                                    "Rate": b['Rate'],
                                    "Unit": b['Unit']['id'],
                                    "UnitName": b['Unit']['BaseUnitConversion'],
                                    "BaseUnitQuantity": b['BaseUnitQuantity'],
                                    "GST": b['GST']['id'],
                                    "HSNCode": b['GST']['HSNCode'],
                                    "GSTPercentage": b['GST']['GSTPercentage'],
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
                                    "DiscountType": b['DiscountType'],
                                    "Discount": b['Discount'],
                                    "DiscountAmount": b['DiscountAmount'],
                                    "BatchCode":BatchCode,
                                    "UnitDetails":UnitDetails
                                   
                                })     
                        OrderData.append({
                            "Supplier": OrderSerializedata[0]['id'],
                            "SupplierName": OrderSerializedata[0]['SupplierName'],
                            "OrderAmount": OrderSerializedata[0]['OrderAmount'],
                            "Customer": OrderSerializedata[0]['CustomerID'],
                            "PriceListId":OrderSerializedata[0]['PriceListId'],
                            "InvoiceNumber":"",
                            "IsSave": IsSave,
                            "OrderItem": OrderItemDetails                            
                    })
                    log_entry = create_transaction_logNew(request, OrderItemSerializedata, OrderSerializedata[0]['CustomerID'],'OrderItemDetails',73,0,0,0,OrderSerializedata[0]['id'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData[0]})
                    
                elif Mode == 2: #Make GRN from VDCChallan                    
                    ChallanQuery = T_Challan.objects.filter(id=POOrderIDs)                    
                    if ChallanQuery.exists():
                        ChallanSerializedata = ChallanSerializerSecond(ChallanQuery, many=True).data  
                        ChallanData = list()
                        for x in ChallanSerializedata:
                            Customer=x['Customer']['id']
                            IsVDCChallan=x['IsVDCChallan']
                            # print(IsVDCChallan)
                            # print(Customer)
                            ChallanItemDetails = list()  
                            if  x['ChallanReferences']:                                                  
                                for D in x['ChallanReferences']: 
                                    DemandID=D['Demands']
                                    # CustomPrint(DemandID)
                                DemandQuery=T_Demands.objects.filter(id=DemandID).values('FullDemandNumber','DemandDate')   
                                FullDemandNumber=DemandQuery[0]['FullDemandNumber']
                                DemandDate=DemandQuery[0]['DemandDate']
                            
                            for y in x['ChallanItems']:
                                print(y)
                                ItemID=y['Item']['id'] 
                                Qty = y['Quantity'] 
                                BillofmaterialData = list() 
                                if IsVDCChallan==1:
                                    # IsVDC= f"and IsVDCItem={IsVDCChallan}"
                                # else:
                                #     IsVDC=""
                                    
                                                            
                                    bomquery = MC_BillOfMaterialItems.objects.raw(f'''SELECT 1 id,MC_BillOfMaterialItems.BOM_id FROM MC_BillOfMaterialItems
                                    JOIN M_BillOfMaterial ON M_BillOfMaterial.id=MC_BillOfMaterialItems.BOM_id
                                    WHERE MC_BillOfMaterialItems.Item_id ={ItemID} and IsDelete=0 AND ISVDCItem=1''') 
                                                                
                                    Query = M_BillOfMaterial.objects.filter(id=bomquery[0].BOM_id)
                                    # print(Query)
                                    BOM_Serializer = M_BOMSerializerSecond001(Query,many=True).data
                                    
                                    
                                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                                    for a in BOM_Serializer:
                                        # if IsVDCChallan==1:
                                            ParentItem=  a['Item']['id'] 
                                else:    
                                    ParentItem=  y['Item']['id']                              
                                Parentquery = MC_ItemUnits.objects.filter(Item_id=ParentItem,IsDeleted=0)
                                # CustomPrint(Parentquery.query)
                                if Parentquery.exists():
                                    ParentUnitdata = Mc_ItemUnitSerializerThird(Parentquery, many=True).data
                                    ParentUnitDetails = list()
                                    for b in ParentUnitdata:
                                        if b['IsDeleted']== 0 :
                                            ParentUnitDetails.append({
                                            "Unit": b['id'],
                                            "UnitName": b['BaseUnitConversion'],
                                            })
                                        
                                GSTquery = M_GSTHSNCode.objects.filter(Item_id=ParentItem,IsDeleted=0)
                                # CustomPrint(GSTquery.query)
                                if GSTquery.exists():
                                    GSTdata =ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                                    GSTDetails = list()
                                    for c in GSTdata:
                                        GSTDetails.append({
                                        "id": c['id'],
                                        "EffectiveDate": c['EffectiveDate'],
                                        "GSTPercentage": c['GSTPercentage'],
                                        "HSNCode": c['HSNCode'],
                                    })
                                MRPquery = M_MRPMaster.objects.filter(Item_id=ParentItem,IsDeleted=0)
                                # CustomPrint(MRPquery.query)
                                if MRPquery.exists():
                                    MRPdata =ItemMRPSerializerSecond(MRPquery, many=True).data
                                    MRPDetails = list()
                                    for d in MRPdata:
                                        MRPDetails.append({
                                        "id": d['id'],
                                        "EffectiveDate": d['EffectiveDate'],
                                        "Company": d['Company']['id'],
                                        "CompanyName": d['Company']['Name'],
                                        "MRP": d['MRP'],
                                        })
                                    
                                if IsVDCChallan==1:
                                    
                                    Item=ParentItem
                                    ItemName=a['Item']['Name']
                                    Unit= a['Unit']['id']
                                    UnitName= a['Unit']['BaseUnitConversion']
                                    BaseUnitQuantity=a['Unit']['BaseUnitQuantity']
                                    BatchCode=SystemBatchCodeGeneration.GetGrnBatchCode(ParentItem, Customer,0)
                                else:
                                    
                                    Item=y['Item']['id']
                                    ItemName=y['Item']['Name']
                                    Unit= y['Unit']['id']
                                    UnitName= y['Unit']['BaseUnitConversion']
                                    BaseUnitQuantity=y['Unit']['BaseUnitQuantity']
                                    BatchCode= y['BatchCode']            
                                BillofmaterialData.append({
                                    "Item":Item,
                                    "ItemName":ItemName,
                                    "Quantity": Qty,
                                    "MRP":MRPDetails[0]['id'],
                                    "MRPValue": MRPDetails[0]['MRP'],
                                    "Rate":y['Rate'], 
                                    "Unit": Unit,
                                    "UnitName": UnitName,
                                    "BaseUnitQuantity": BaseUnitQuantity,
                                    "GST":GSTDetails[0]['id'],
                                    "HSNCode": GSTDetails[0]['HSNCode'],
                                    "GSTPercentage": GSTDetails[0]['GSTPercentage'],
                                    "Margin": "",
                                    "MarginValue":"",
                                    "BasicAmount": "",
                                    "GSTAmount": "",
                                    "CGST": "",
                                    "SGST": "",
                                    "IGST": "",
                                    "CGSTPercentage": "",
                                    "SGSTPercentage": "",
                                    "IGSTPercentage": "",
                                    "Amount":"",
                                    "BatchCode":BatchCode,
                                    "LoginName":"",
                                    "UnitDetails":ParentUnitDetails                                       
    
                                    })       
                                ChallanItemDetails.append(BillofmaterialData[0])        
                        ChallanData.append({
                            "Supplier": x['Party']['id'],
                            "SupplierName": x['Customer']['Name'],
                            "OrderAmount": x['GrandTotal'],
                            "Customer": x['Customer']['id'],
                            "InvoiceNumber":" ",
                            "IsSave": 0,                            
                            "FullDemandNumber":x['FullChallanNumber'],
                            "DemandDate":x['ChallanDate'],
                            "OrderItem": ChallanItemDetails,
                        })
                        # CustomPrint("SPPPPPP")
                        # CustomPrint(ChallanItemDetails)
                        log_entry = create_transaction_logNew(request,ChallanSerializedata, 0,'ChallanData',74,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ChallanData[0]})
                    
                elif Mode == 3: #Make GRN from Invoice
                    
                    Query1 = T_Invoices.objects.filter(id=POOrderIDs).values('Customer')
                    
                    # CustomPrint(str(Query1[0]['Customer'])) 
                    
                    Query = T_Invoices.objects.filter(id=POOrderIDs).select_related('Party').values('Party__PartyType_id')
                    # CustomPrint(str(Query[0]['Party__PartyType_id'])) 
                    if (Query[0]['Party__PartyType_id']) ==12:
                        IsDivisionFlag=1
                    else:
                        IsDivisionFlag=0
                        
                        
                
                    Ord=TC_InvoicesReferences.objects.filter(Invoice_id=POOrderIDs).values('Order')
                    
                    if Ord.exists():
                        
                        Invoiceid=Ord[0]['Order']       
                        OrderQuery=T_Orders.objects.filter(id=Invoiceid).values('FullOrderNumber')   
                        FullOrderNumber=OrderQuery[0]['FullOrderNumber']
                    else:
                        FullOrderNumber=0
                    InvoiceQuery = T_Invoices.objects.filter(id=POOrderIDs)
                    
                    if InvoiceQuery.exists():
                        InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                        # CustomPrint(InvoiceSerializedata)
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                        InvoiceData = list()
                        for a in InvoiceSerializedata:
                            InvoiceItemDetails = list()                           
                              
                            for b in a['InvoiceItems']:
                                checkitemassigninPartyItems=MC_PartyItems.objects.filter(Item=b['Item']['id'],Party=a['Customer']['id']).count()
                                if checkitemassigninPartyItems > 0:
                                    PartyItemAssign = True
                                else:
                                    PartyItemAssign = False
                                    
                                if IsDivisionFlag == 1:
                                    # CustRate=RateCalculationFunction(0,b['Item']['id'],Query1[0]['Customer'],0,0,b['Unit']["id"],0,0).RateWithGST()
                                    # Rate=CustRate[0]["RateWithoutGST"]
                                    CustRate= TC_InvoiceItems.objects.raw(f'''select 1 as id, ifnull(RateCalculationFunction1(0, {b['Item']['id']}, {Query1[0]['Customer']}, 0, {b['Unit']['id']}, 0, 0, 0),0) Rate''')
                                    Rate =round(CustRate[0].Rate,2)
                                else:
                                    Rate = b['Rate']
                                    
                                Item= b['Item']['id']
                                query = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                                # CustomPrint(query.query)
                                if query.exists():
                                    Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                                    UnitDetails = list()
                                    for c in Unitdata:
                                        if c['IsDeleted']== 0 :
                                            UnitDetails.append({
                                            "Unit": c['id'],
                                            "UnitName": c['BaseUnitConversion'],
                                        })
                                # MRPquery = M_MRPMaster.objects.filter(Item_id=b['Item']['id']).order_by('-id') 
                                
                                MRPquery=MRPListFun(Item,a['Customer']['id'],0)        
                                if MRPquery.exists():
                                    # MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                                    ItemMRPDetails = list()
                                    unique_MRPs = set()
                                    for d in MRPquery:
                                        MRPs = d['MRP']
                                        if MRPs not in unique_MRPs:
                                            ItemMRPDetails.append({
                                                "MRP": d['id'],
                                                "MRPValue": MRPs,  
                                            })
                                            unique_MRPs.add(MRPs)        
                                        
                                # GSTquery = M_GSTHSNCode.objects.filter(Item_id=b['Item']['id']).order_by('-id')[:3]
                                GSTquery=GSTListFun(Item,a['Customer']['id'],0) 
                                if GSTquery.exists():
                                    # Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                                    ItemGSTDetails = list()
                                    for e in GSTquery:
                                        ItemGSTDetails.append({
                                        "GST": e['id'],
                                        "GSTPercentage": e['GSTPercentage'],   
                                    })
                                    
                                         
                                InvoiceItemDetails.append({
                                    "Item": b['Item']['id'],
                                    "ItemName": b['Item']['Name'],
                                    "Quantity": b['Quantity'],
                                    "QtyInBox": round(float(b['QtyInBox']),2),
                                    "MRPDetails": ItemMRPDetails,
                                    "Rate": Rate,
                                    "TaxType": b['TaxType'],
                                    "Unit": b['Unit']['id'],
                                    "UnitName": b['Unit']['BaseUnitConversion'],
                                    "BaseUnitQuantity": b['BaseUnitQuantity'],
                                    "GSTDropdown":ItemGSTDetails,
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
                                    "DiscountType": b['DiscountType'],
                                    "Discount": b['Discount'],
                                    "DiscountAmount": b['DiscountAmount'],
                                    "UnitDetails":UnitDetails,
                                    "MRP":b['MRP']['id'],
                                    "MRPValue":b['MRPValue'],
                                    "PartyItemAssign":PartyItemAssign 
                                })
                                
                            InvoiceData.append({
                                "Supplier": a['Party']['id'],
                                "SupplierName": a['Party']['Name'],
                                "OrderAmount": a['GrandTotal'],
                                "Customer": a['Customer']['id'],
                                "InvoiceNumber":a['FullInvoiceNumber'],
                                "IsSave": 0,  
                                "FullOrderNumber":FullOrderNumber,
                                "OrderItem": InvoiceItemDetails,
                                
                                
                            })
                        log_entry = create_transaction_logNew(request,InvoiceSerializedata, a['Party']['id'],'Supplier:'+str(a['Party']['id']),75,0,0,0,a['Customer']['id'])
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]}) 
                elif Mode == 4: #Make GRN from Challan
                    
                    ChallanQuery = T_Challan.objects.filter(id=POOrderIDs)                    
                    if ChallanQuery.exists():
                        ChallanSerializedata = ChallanSerializerSecond(ChallanQuery, many=True).data                                         
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ChallanSerializedata})
                        
                        ChallanData = list()
                        for x in ChallanSerializedata:
                            ChallanItemDetails = list()                                                  
                            for D in x['ChallanReferences']: 
                                DemandID=D['Demands']                               
                            DemandQuery=T_Demands.objects.filter(id=DemandID).values('FullDemandNumber','DemandDate')   
                            FullDemandNumber=DemandQuery[0]['FullDemandNumber']
                            DemandDate=DemandQuery[0]['DemandDate']                            
                            for y in x['ChallanItems']:                                
                                    Qty = y['Quantity']                                
                                # bomquery = MC_BillOfMaterialItems.objects.filter(Item_id=y['Item']['id']).values('BOM')                                
                                # Query = M_BillOfMaterial.objects.filter(id=bomquery[0]['BOM'])                                
                                # BOM_Serializer = M_BOMSerializerSecond001(Query,many=True).data                                
                                    BillofmaterialData = list()
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                                # for a in BOM_Serializer:
                                    ParentItem= y['Item']['id']                                    
                                    Parentquery = MC_ItemUnits.objects.filter(Item_id=ParentItem,IsDeleted=0)                                    
                                    if Parentquery.exists():
                                        ParentUnitdata = Mc_ItemUnitSerializerThird(Parentquery, many=True).data
                                        ParentUnitDetails = list()
                                        for b in ParentUnitdata:
                                            if b['IsDeleted']== 0 :
                                                ParentUnitDetails.append({
                                                "Unit": b['id'],
                                                "UnitName": b['BaseUnitConversion'],
                                                })
                                            
                                    GSTquery = M_GSTHSNCode.objects.filter(Item_id=ParentItem,IsDeleted=0)                                    
                                    if GSTquery.exists():
                                        GSTdata =ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                                        GSTDetails = list()
                                        for c in GSTdata:
                                            GSTDetails.append({
                                            "id": c['id'],
                                            "EffectiveDate": c['EffectiveDate'],
                                            "GSTPercentage": c['GSTPercentage'],
                                            "HSNCode": c['HSNCode'],
                                        })
                                    MRPquery = M_MRPMaster.objects.filter(Item_id=ParentItem,IsDeleted=0)                                    
                                    if MRPquery.exists():
                                        MRPdata =ItemMRPSerializerSecond(MRPquery, many=True).data
                                        MRPDetails = list()
                                        for d in MRPdata:
                                            MRPDetails.append({
                                            "id": d['id'],
                                            "EffectiveDate": d['EffectiveDate'],
                                            "Company": d['Company']['id'],
                                            "CompanyName": d['Company']['Name'],
                                            "MRP": d['MRP'],
                                            })                
                                    BillofmaterialData.append({
                                        "Item":ParentItem,
                                        "ItemName":y['Item']['Name'],
                                        "Quantity": Qty,
                                        "MRP":MRPDetails[0]['id'],
                                        "MRPValue": MRPDetails[0]['MRP'],
                                        "Rate":y['Rate'], 
                                        "Unit": y['Unit']['id'],
                                        "UnitName": y['Unit']['BaseUnitConversion'],
                                        "BaseUnitQuantity": y['Unit']['BaseUnitQuantity'],
                                        "GST":GSTDetails[0]['id'],
                                        "HSNCode": GSTDetails[0]['HSNCode'],
                                        "GSTPercentage": GSTDetails[0]['GSTPercentage'],
                                        "Margin": "",
                                        "MarginValue":"",
                                        "BasicAmount":y['BasicAmount'],
                                        "GSTAmount": y['GSTAmount'],
                                        "CGST": y['CGST'],
                                        "SGST": y['SGST'],
                                        "IGST": y['IGST'],
                                        "CGSTPercentage": y['CGSTPercentage'],
                                        "SGSTPercentage":y['SGSTPercentage'],
                                        "IGSTPercentage": y['IGSTPercentage'],
                                        "Amount":y['Amount'],
                                        "BatchCode":y['BatchCode'],
                                        "LoginName":"",
                                        "UnitDetails":ParentUnitDetails   
                                        })       
                                    ChallanItemDetails.append(BillofmaterialData[0])        
                        ChallanData.append({
                            "Supplier": x['Party']['id'],
                            "SupplierName": x['Customer']['Name'],
                            "OrderAmount": x['GrandTotal'],
                            "Customer": x['Customer']['id'],
                            "InvoiceNumber":" ", 
                            "IsSave": 0,                            
                            "FullDemandNumber":FullDemandNumber,
                            "DemandDate":DemandDate,
                            "OrderItem": ChallanItemDetails,
                        })
                        # CustomPrint("SPPPPPP")
                        # CustomPrint(ChallanItemDetails)
                        log_entry = create_transaction_logNew(request,ChallanSerializedata, 0,'ChallanData',74,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ChallanData[0]})   
                else:
                    log_entry = create_transaction_logNew(request, InvoiceSerializedata, a['Party']['id'],'Data Not available',7,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})   
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'MakeOrdersGrn:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
    
#GRN Save for CSS

class GRNSaveforCSSView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        GRNdata = JSONParser().parse(request)
        try: 
            if 'InvoiceNumber' not in GRNdata or not GRNdata['InvoiceNumber']:
                return JsonResponse({'StatusCode': 406, 'Status': False, 'Message': 'InvoiceNumber is Required', 'Data': []})
            
            Customer = GRNdata['Customer']
            InvoiceNumber = GRNdata['InvoiceNumber']
            InvoiceDate = GRNdata['InvoiceDate']
            
            ExistingGRN = T_GRNs.objects.filter(Customer_id=Customer, InvoiceNumber=InvoiceNumber, InvoiceDate=InvoiceDate).exists()
            if ExistingGRN:
                log_entry = create_transaction_logNew(request, GRNdata, 0, 'GRN already exists with the provided details. Do you want to continue?', 440, 0)
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'GRN already exists with the provided details. Do you want to continue?', 'Data': []})
            log_entry = create_transaction_logNew(request, GRNdata, 0, '', 440, 0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GRN can be saved', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, GRNdata, 0, 'GRNSaveforCSS:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})





class DeleteAccountingGRNView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request):
        AccountDetails= JSONParser().parse(request)
       
        try:
            with transaction.atomic():
                DeletedGRN_id=AccountDetails['GRNid']
                # print(DeletedGRN_id)
                GRN = T_GRNs.objects.get(id=DeletedGRN_id) 
                # print(GRN)
                #GRN record update (ISSave=1, TotalExpenses=0)
                GRN.IsSave = 1
                GRN.TotalExpenses = 0
                # GRN.save()
                # #GRNItems update - AccountingQuantity = 0
                # TC_GRNItems.objects.filter(GRN=DeletedGRN_id).update(AccountingQuantity=0)
                # # GRNExpenses delete record
                # TC_GRNExpenses.objects.filter(GRN_id=DeletedGRN_id).delete()
                log_entry =create_transaction_logNew(request, {'GRNID': DeletedGRN_id}, 0, 'Accounting GRN marked as deleted', 457, 0)
                return JsonResponse({'StatusCode': 200,'Status': True,'Message': 'Accounting GRN marked as deleted.','Data': []})

        except T_GRNs.DoesNotExist:
            log_entry = create_transaction_logNew(request, {'GRNID': DeletedGRN_id}, 0, '', 457, 0)
            return JsonResponse({'StatusCode': 204,'Status': False,'Message': 'GRN not found.','Data': []})
        except Exception as e:
            log_entry =create_transaction_logNew(request, {'GRNID': DeletedGRN_id}, 0, 'Error updating GRN: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400,'Status': False,'Message': str(e),'Data': [] })