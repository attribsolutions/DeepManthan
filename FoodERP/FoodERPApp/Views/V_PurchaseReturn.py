import json
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix, SystemBatchCodeGeneration
from ..Serializer.S_CreditDebit import *
from ..Serializer.S_Items import *
from ..Serializer.S_GRNs import *
from django.db.models import Sum
from ..models import *
import datetime
import base64
from io import BytesIO
from PIL import Image



class PurchaseReturnListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Returndata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                FromDate = Returndata['FromDate']
                ToDate = Returndata['ToDate']
                Customer = Returndata['CustomerID']
                Party = Returndata['PartyID']

                if(Customer == ''):
                    cust=Q()
                else:
                    cust=Q(Customer=Customer) 
                
                if(Party == ''):
                    par=Q()
                else:
                    par=Q(Party=Party)

                # for log
                if (Party == ''):
                    x = 0
                    y = Customer
                    log_entry = create_transaction_logNew(request, Returndata, y,'From:'+FromDate+','+'To:'+ToDate,51,0,FromDate,ToDate,0)

                elif (Customer == ''):
                    x = Party
                    y = 0
                    log_entry = create_transaction_logNew(request, Returndata, x,'From:'+FromDate+','+'To:'+ToDate,51,0,FromDate,ToDate,0)

                else:
                    x = Party
                    y = Customer      
                    log_entry = create_transaction_logNew(request, Returndata, x,'From:'+FromDate+','+'To:'+ToDate,238,0,FromDate,ToDate,y)
          
                query = T_PurchaseReturn.objects.filter(ReturnDate__range=[FromDate, ToDate]).filter( cust ).filter(par)
                
                # CustomPrint(query.query)
                if query:
                    Return_serializer = PurchaseReturnSerializerSecond(query, many=True).data
                    ReturnListData = list()
                    for a in Return_serializer:
                        q0=TC_PurchaseReturnReferences.objects.filter(SubReturn=a['id'])
                        q1= TC_ReceiptInvoices.objects.raw(''' select 1 id,count(*)cnt from TC_ReceiptInvoices 
join T_CreditDebitNotes on T_CreditDebitNotes.id=TC_ReceiptInvoices.CRDRNote_id
where TC_ReceiptInvoices.Return_id=%s and T_CreditDebitNotes.IsDeleted=0 ''' ,[a['id']])
                        for countrow in q1:
                            p=countrow.cnt
                        if p > 0:
                            IsCreditNoteCreated = 1
                        else:    
                            IsCreditNoteCreated = 0 
                        
                        
                        if q0.count() > 0:
                            IsSendToSS = 1
                        else:
                            IsSendToSS = 0

                        if (IsSendToSS == 1):
                            Status = "Send To Supplier"
                            
                        elif a["IsApproved"] == 1: 
                            
                            Status = "Approved" 
                        elif a["IsApproved"] == 2:
                            Status = "Reject"
                        else:    
                            Status = "Open" 
                        PurchaseReturnUpload_serializer = list()
                        PurchaseReturnUpload = TC_PurchaseReturnUploads.objects.filter(PurchaseReturn=a["id"])
                        PurchaseReturnUpload_serializer = PurchaseReturnUploadsSerializer(PurchaseReturnUpload, many=True).data
                        ReturnListData.append({
                            "id": a['id'], 
                            "ReturnDate": a['ReturnDate'],
                            "ReturnNo": a['ReturnNo'],
                            "FullReturnNumber": a['FullReturnNumber'],
                            "ReturnReasonID":a['ReturnReason']['id'],
                            "ReturnReasonName":a['ReturnReason']['Name'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "PartyTypeID": a['Party']['PartyType'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "IsApproved" :a["IsApproved"],
                            "Comment" :a["Comment"],
                            "Status" :Status,
                            "Mode":a["Mode"],
                            "ASMApprovalImgUpload":a["ASMApprovalImgUpload"],
                            "IsCreditNoteCreated" : IsCreditNoteCreated,
                            "InvoiceUploads":PurchaseReturnUpload_serializer
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReturnListData})
                log_entry = create_transaction_logNew(request, Returndata, x, 'Return List Not Found',51,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PuchaseReturnList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

def primarySourceNAme(ID,returnID):
    if ID is None:
        PrimartSource =''
    else:    
        
        q1=TC_PurchaseReturnItems.objects.filter(id=ID).values('PurchaseReturn_id')
        
        b=q1[0]['PurchaseReturn_id']
       
        q2=T_PurchaseReturn.objects.raw('''SELECT T_PurchaseReturn.id, concat((select FullReturnNumber from T_PurchaseReturn where id= %s  ), ' : ' ,supl.Name,'-(',cust.Name,')') PrimartSource
    FROM T_PurchaseReturn 
    join M_Parties cust on cust.id=T_PurchaseReturn.Customer_id
    join M_Parties supl on supl.id=T_PurchaseReturn.Party_id
    where T_PurchaseReturn.id=%s''',[returnID,b])
        
        for row in q2:
            PrimartSource = row.PrimartSource
        
    return PrimartSource

class PurchaseReturnView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser,MultiPartParser,FormParser]
    # authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Query = T_PurchaseReturn.objects.filter(id=id)
                
                if Query.exists():
                    PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query, many=True, context= {'request': request}).data 
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PurchaseReturnSerializer})
                    PuchaseReturnList=list()

                    for a in PurchaseReturnSerializer:
                        PurchaseReturnItemList=list()
                        for b in a['ReturnItems']:
                            
                            ReturnItemImagesList=list()
                            for c in b['ReturnItemImages']:
                                ReturnItemImagesList.append({
                                    "Image":c['Image']
                                })
                            
                            
                            
                            PurchaseReturnItemList.append({
                                "id":b['id'],
                                "ItemComment":b['ItemComment'],
                                "Quantity":b['Quantity'],
                                "BaseUnitQuantity":b['BaseUnitQuantity'],
                                "MRPValue":b['MRPValue'],
                                "Rate":b['Rate'],
                                "BasicAmount":b['BasicAmount'],
                                "TaxType":b['TaxType'],
                                "GSTPercentage":b['GSTPercentage'],
                                "GSTAmount":b['GSTAmount'],
                                "Amount":b['Amount'],
                                "CGST":b['CGST'],
                                "SGST":b['SGST'],
                                "IGST":b['IGST'],
                                "CGSTPercentage":b['CGSTPercentage'],
                                "SGSTPercentage":b['SGSTPercentage'],
                                "IGSTPercentage":b['IGSTPercentage'],
                                "BatchDate":b['BatchDate'],
                                "BatchCode":b['BatchCode'],
                                "CreatedOn":b['CreatedOn'],
                                "GST":b['GST'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'],
                                "MRP":b['MRP'],
                                "PurchaseReturn":b['PurchaseReturn'],
                                "Unit":b['Unit']['id'],
                                "UnitName" : b['Unit']['UnitID']['Name'],
                                "ItemReasonID":b['ItemReason']['id'],
                                "ItemReason":b['ItemReason']['Name'],
                                "Comment":b['Comment'],
                                "DiscountType":b['DiscountType'],
                                "Discount":b['Discount'],
                                "DiscountAmount":b['DiscountAmount'],
                                "ApprovedQuantity":b['ApprovedQuantity'],
                                "primarySourceID" : b["primarySourceID"],
                                "ApprovedByCompany" : b["ApprovedByCompany"],
                                "primarySource" : primarySourceNAme(b["primarySourceID"],b['SubReturn']),
                                "ReturnItemImages":ReturnItemImagesList
                            })
                        
                        PuchaseReturnList.append({
                            "ReturnDate":a['ReturnDate'],
                            "ReturnNo":a['ReturnNo'],
                            "FullReturnNumber":a['FullReturnNumber'],
                            "GrandTotal":a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Comment":a['Comment'],
                            "CreatedOn":a['CreatedOn'],
                            "UpdatedOn":a['UpdatedOn'],
                            "Customer":a['Customer']['id'],
                            "CustomerName":a['Customer']['Name'],
                            "Party":a['Party'],
                            "ReturnReason":a['ReturnReason'],
                            "IsApproved" : a["IsApproved"],
                            "ReturnItems":PurchaseReturnItemList
                        })
                        
                        log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, a['Party'],'ReturnDate:'+a['ReturnDate']+','+'Supplier:'+str(a['Party']),52,0,0,0,int(a['Customer']['id']))
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PuchaseReturnList})
                log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, a['Party'], 'PurchaseReturn not available',52,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PurchaseReturnDetails:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def post(self, request,format=None):
        try:
            
            with transaction.atomic():
                
                '''Image Upload Code start'''
                # Assuming these fields are JSON arrays in the POST data
                purchase_return_references_json = request.POST.get('PurchaseReturnReferences')
                return_items_json = request.POST.get('ReturnItems')
                # Parse JSON arrays into Python lists
                purchase_return_references = json.loads(purchase_return_references_json) if purchase_return_references_json else []
                return_items = json.loads(return_items_json) if return_items_json else []
                PurchaseReturndata = {
                    "ReturnDate" : request.POST.get('ReturnDate'),
                    "ReturnReasonOptions" : request.POST.get('ReturnReasonOptions'),
                    "BatchCode" : request.POST.get('BatchCode'),
                    "Customer" : request.POST.get('Customer'),
                    "Party" : request.POST.get('Party'),
                    "Comment" : request.POST.get('Comment'),
                    "GrandTotal" : request.POST.get('GrandTotal'),
                    "RoundOffAmount" : request.POST.get('RoundOffAmount'),
                    "CreatedBy" : request.POST.get('CreatedBy'),
                    "UpdatedBy" : request.POST.get('UpdatedBy'),
                    "IsApproved" : request.POST.get('IsApproved'),
                    "Mode" : request.POST.get('Mode'),
                    "Vehicle":request.POST.get('Vehicle'),
                    "PurchaseReturnReferences" : purchase_return_references,
                    "ReturnItems" : return_items
                } 
                
                '''Image Upload code END'''
                # PurchaseReturndata = JSONParser().parse(request)
                Party = PurchaseReturndata['Party']
                Date = PurchaseReturndata['ReturnDate']
                Mode = PurchaseReturndata['Mode'] 
                customerid=PurchaseReturndata['Customer']
               
                c = GetMaxNumber.GetPurchaseReturnNumber(Party,Date)
                
                PurchaseReturndata['ReturnNo'] = str(c)               
               
                if (Mode == str(1)): # Sales Return    
                    # d= 'SRN'
                    d = GetPrifix.GetPurchaseReturnPrifix(Party) 
                else :                   
                    d = GetPrifix.GetPurchaseReturnPrifix(customerid)  
                 
                #  comment for Prifix get None
                # PurchaseReturndata['FullReturnNumber'] = str(d)+""+str(c)
                PurchaseReturndata['FullReturnNumber'] = (str(d) if d is not None else "") + str(c)
                # print("PurchaseReturndata",PurchaseReturndata)
                
                item = ""
                
                query = T_PurchaseReturn.objects.filter(Party_id=Party).values('id')
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                UpdateO_BatchWiseLiveStockList = list()
                
                for a in PurchaseReturndata['ReturnItems']:
                    
                    '''Image Upload Code End''' 
                    keyname='uploaded_images_'+str(a['Item'])
                    avatar = request.FILES.getlist(keyname)
                    for img,file in zip(a['ReturnItemImages'],avatar):
                        img['Image']=file 
                       
                    '''Image Upload Code End'''
            
                    SaleableItemReason=MC_SettingsDetails.objects.filter(SettingID=14).values('Value')
                    value_str = SaleableItemReason[0]['Value']
                    # Split the string by ',' and convert the resulting substrings to integers
                    values_to_check = [int(val) for val in value_str.split(',')]
                    if a['ItemReason'] in values_to_check:
                        IsDamagePieces =False
                    else:
                        IsDamagePieces =True
                             
                    query1 = TC_PurchaseReturnItems.objects.filter(Item_id=a['Item'], BatchDate=date.today(), PurchaseReturn_id__in=query).values('id')
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                    
                    if(item == ""):
                        item = a['Item']
                        b = query1.count()

                    elif(item == a['Item']):
                        item = 1
                        b = b+1
                    else:
                        item = a['Item']
                        b = 0
                        
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'],Party, b)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = BaseUnitQuantity
                       
                    O_BatchWiseLiveStockList.append({
                    "id":a['BatchID'],    
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Party,
                    "IsDamagePieces":IsDamagePieces,
                    "CreatedBy":PurchaseReturndata['CreatedBy']
                    
                    })
                    
                    # Sales Returnconsoldated Stock Minus When Send to Supplier AND Self Purchase Return 
                    UpdateO_BatchWiseLiveStockList.append({
                    "id":a['BatchID'],    
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "PurchaseReturn":a['PurchaseReturn'],
                    })

                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "MRPValue": a['MRPValue'],
                    "Rate": a['Rate'],
                    "GST": a['GST'],
                    "GSTPercentage": a['GSTPercentage'],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList,
                    "UpdateO_BatchWiseLiveStockList":UpdateO_BatchWiseLiveStockList                   
                    
                    })
                    O_BatchWiseLiveStockList=list()
                    UpdateO_BatchWiseLiveStockList = list()
              
                PurchaseReturndata.update({"O_LiveBatchesList":O_LiveBatchesList}) 
                PurchaseReturn_Serializer = PurchaseReturnSerializer(data=PurchaseReturndata)
                # print(PurchaseReturn_Serializer)
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn = PurchaseReturn_Serializer.save()
                    LastInsertID = PurchaseReturn.id
                    if Mode == str(1): #SalesReturn
                        
                        log_entry = create_transaction_logNew(request, PurchaseReturndata,Party,'ReturnDate:'+PurchaseReturndata['ReturnDate']+','+'Customer:'+str(PurchaseReturndata['Customer'])+','+'TransactionID:'+str(LastInsertID),239,LastInsertID,0,0,PurchaseReturndata['Customer'])
                    elif Mode == str(2): #PurchaseReturn
                        
                        log_entry = create_transaction_logNew(request, PurchaseReturndata,PurchaseReturndata['Customer'],'ReturnDate:'+PurchaseReturndata['ReturnDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastInsertID),53,LastInsertID,0,0,Party)
                    elif Mode == str(3):
                        
                        log_entry = create_transaction_logNew(request, PurchaseReturndata,Party,'ReturnDate:'+PurchaseReturndata['ReturnDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastInsertID),53,LastInsertID,0,0,PurchaseReturndata['Customer'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Save Successfully', 'TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, PurchaseReturndata, PurchaseReturndata['Customer'],'ReturnSave:'+str(PurchaseReturn_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PurchaseReturnSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
    
    # Purchase Return DELETE API New code Date 25/07/2023
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Query = T_PurchaseReturn.objects.filter(id=id).values('Mode')
                Mode = str(Query[0]['Mode'])
                if Mode == '1':   # Sales Return Mode
                    PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
                    PurchaseReturn_Data.delete()
                    log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, 0, '',54,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []})
                else:
                    Query2 = T_PurchaseReturn.objects.filter(id=id)
                    if Query2.exists():
                        PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query2, many=True).data 
                        for a in PurchaseReturnSerializer:
                            for b in a['ReturnItems']:
                                Qty =0.00
                                if Mode == '2': # Purchase Return Mode 
                                    OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
                                else:    
                                    OBatchQuantity=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
                                Qty=float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
                                if(OBatchQuantity[0]['OriginalBaseUnitQuantity'] >= float(Qty)):
                                    if Mode == '2': # Purchase Return Mode
                                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) 
                                    else:
                                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) #float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
                                    Qty =0.00
                                else:    
                                    log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, 0, 'PurchaseReturnID:'+str(id),55,0)
                                    return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Return Qty greater than Consolidated return qty', 'Data': []})     
                        PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
                        PurchaseReturn_Data.delete()  
                        log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, 0, 'PurchaseReturnID:'+str(id),54,0)      
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []}) 
        except IntegrityError:
            log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, 0, 'PurchaseReturnID:'+str(id),8,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PurchaseReturnDelete:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []}) 
    
    #Purchase Return Delete API code Date Working code  Date 24/07/2023
    
    # @transaction.atomic()
    # def delete(self, request, id=0):
    #     try:
    #         with transaction.atomic():
    #             Query = TC_PurchaseReturnReferences.objects.filter(PurchaseReturn=id)
    #             if Query:
    #                 Query2 = T_PurchaseReturn.objects.filter(id=id)
    #                 if Query2.exists():
    #                     PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query2, many=True).data 
    #                     for a in PurchaseReturnSerializer:
    #                         for b in a['ReturnItems']:
    #                             Qty =0.00 
    #                             OBatchQuantity=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
    #                             Qty=float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
    #                             if(OBatchQuantity[0]['OriginalBaseUnitQuantity'] >= float(Qty)):
    #                                 OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) #float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
    #                                 Qty =0.00
    #                             else:    
    #                                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Qty greater than Consolidated return qty', 'Data': []})     
    #                     PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
    #                     PurchaseReturn_Data.delete()        
    #                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []}) 
    #             else:
    #                 Query = T_PurchaseReturn.objects.filter(id=id).values('Mode')
    #                 if str(Query[0]['Mode'])== '2':
    #                     Query = T_PurchaseReturn.objects.filter(id=id)
    #                     PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query, many=True).data
    #                     for a in PurchaseReturnSerializer:
                            
    #                         for b in a['ReturnItems']:
    #                             Qty =0.00
    #                             OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
    #                             Qty=float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
    #                             if(OBatchQuantity[0]['OriginalBaseUnitQuantity'] >= float(Qty)):
    #                                 OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) 
    #                                 Qty =0.00
    #                             else:    
    #                                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Qty greater than Consolidated return qty', 'Data': []})
    #                     PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
    #                     PurchaseReturn_Data.delete()    
    #                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []})
    #                 else:
    #                     PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
    #                     PurchaseReturn_Data.delete()
    #                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []}) 
    #     except IntegrityError:
    #         return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
    #     except Exception as e:
    #         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})                 
        
##################### Purchase Return Item View ###########################################        
        
class ReturnItemAddView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0,Party=0):
        try:
            with transaction.atomic():
                # query = M_Items.objects.filter(id=id).values('id','Name')
                query = M_Items.objects.raw('''select id ,name ,
                                                round(GetTodaysDateMRP(%s,curdate(),2,0,0,0),2)MRPValue,                                                
                                                round(GetTodaysDateRate(%s,curdate(),0,0,2,0),2)RateValue,
                                                round(GSTHsnCodeMaster(%s,curdate(),2,0,0),2)GSTPercentage,
                                                GetTodaysDateMRP(%s,curdate(),1,0,0,0)MRPID,
                                                GSTHsnCodeMaster(%s,curdate(),1,0,0)GSTID,
                                                GetTodaysDateRate(%s,curdate(),0,0,1,0)RateID
                                                from M_Items where id =%s''',[id,id,id,id,id,id,id])
                # CustomPrint(query.query)
                
                if query:
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    # Itemsdata = M_ItemsSerializer02(query, many=True).data
                    # return JsonResponse({'query':  Itemsdata})
                    Itemlist = list()
                    InvoiceItems=list()
                    ItemGSTDetails = list()
                    ItemMRPDetails = list()
                    ItemRateDetails=list()
                    for a in query:
                        Item=a.id
                        ItemMRPDetails.append({
                                        "MRP": a.MRPID,
                                        "MRPValue": a.MRPValue,
                                    })
                        ItemRateDetails.append({
                                        "Rate": a.RateID,
                                        "RateValue": a.RateValue,
                                         })                        
                        
                        ItemGSTDetails.append({
                                "GST": a.GSTID,
                                "GSTPercentage": a.GSTPercentage,   
                            })
                        
                        Unitquery = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                        if Unitquery.exists():
                            Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                            ItemUnitDetails = list()
                            for c in Unitdata:
                                ItemUnitDetails.append({
                                "Unit": c['id'],
                                "BaseUnitQuantity": c['BaseUnitQuantity'],
                                "IsBase": c['IsBase'],
                                "UnitName": c['BaseUnitConversion'],
                            })

                        
                        # MRPquery = M_MRPMaster.objects.filter(Item_id=Item).order_by('-id')
                        # if MRPquery.exists():
                        #     MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                        #     ItemMRPDetails = list()
                        #     unique_MRPs = set()
                            
                        #     for d in MRPdata:
                        #         MRPs = d['MRP']
                        #         if MRPs not in unique_MRPs:
                        #             ItemMRPDetails.append({
                        #                 "MRP": d['id'],
                        #                 "MRPValue": MRPs,
                        #             })
                        #             unique_MRPs.add(MRPs)
                        
                        # GSTquery = M_GSTHSNCode.objects.filter(Item_id=Item).order_by('-id')[:3] 
                        # if GSTquery.exists():
                        #     Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                            
                        #     for e in Gstdata:
                        #         ItemGSTDetails.append({
                        #         "GST": e['id'],
                        #         "GSTPercentage": e['GSTPercentage'],   
                        #     }) 
                        InvoiceItems.append({
                            "Item": a.id,
                            "ItemName": a.Name,
                            "ItemUnitDetails": ItemUnitDetails, 
                            "ItemMRPDetails":ItemMRPDetails,
                            "ItemGSTDetails":ItemGSTDetails,
                            "ItemRateDetails":ItemRateDetails
                        })
                    
                    Itemlist.append({"InvoiceItems":InvoiceItems}) 
                    log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, 0,'',56,0)   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Itemlist[0]})
                log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, 0, 'ReturnItemList Not available',56,0)   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, 0, 'ReturnItemList Not available',56,0) 
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'ReturnItemAdd:'+str(e),33,0) 
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})        



class ReturnItemBatchCodeAddView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)
                ItemID = PurchaseReturndata['ItemID']
                BatchCode = PurchaseReturndata['BatchCode']
                CustomerID =PurchaseReturndata['Customer']
                PartyID = PurchaseReturndata['Party']
                
                Itemquery = M_Items.objects.filter(id=ItemID).values("id","Name")
                Item =Itemquery[0]["id"]
                # Unitquery = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0,UnitID_id=1).values("id")
                # print(Unitquery.query)
                CssCompanyID=M_Settings.objects.filter(id=61).values("DefaultValue")
                CssCompany=str(CssCompanyID[0]['DefaultValue'])                        
                if int(CssCompany)==4:                            
                    with connection.cursor() as cursor:
                        cursor.execute(f'''
                            SELECT ROUND(GetTodaysDateRate({ItemID}, CURDATE(), {PartyID}, 0, 2), 2) AS VRate
                        ''')
                        row = cursor.fetchone() 
                    Rate=row[0] if row else None                           
                    filter_unit = {"Item_id": ItemID, "IsDeleted": 0,"IsBase":1}                         
                else:
                    Rate = ""       
                    filter_unit = {"Item_id": ItemID, "IsDeleted": 0, "UnitID_id": 1}

                Unitquery = MC_ItemUnits.objects.filter(**filter_unit).values("id","UnitID__Name") 
                # print(Unitquery.query)                
                # MRPquery = M_MRPMaster.objects.filter(Item_id=Item ).order_by('-id')
                # if not MRPquery:
                #     MRPquery = M_MRPMaster.objects.filter(Item_id=Item ).order_by('-id')
                
                MRPquery=MRPListFun(Item,CustomerID,0)
                # print(MRPquery)
                if MRPquery.exists():                    
                    # MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                    ItemMRPDetails = list()
                    unique_MRPs = set()
                    for d in MRPquery:
                        MRPs = d['MRP']
                        # print(MRPs)
                        if int(CssCompany)!=4:
                           CalculatedRateusingMRPMargin1=M_Items.objects.raw(f'''select 1 as id,RateCalculationFunction1(0, {Item}, {CustomerID}, 1, 0, 0, {MRPs}, 0)RatewithoutGST''')
                           Rate=round(CalculatedRateusingMRPMargin1[0].RatewithoutGST,2)
                        else:
                            Rate=Rate
                        
                        # CalculatedRateusingMRPMargin=RateCalculationFunction(0,Item,CustomerID,0,1,0,0,MRPs).RateWithGST()
                        # Rate=CalculatedRateusingMRPMargin[0]["NoRatewithOutGST"]
                        if MRPs not in unique_MRPs:
                            ItemMRPDetails.append({
                                "MRP": d['id'],
                                "MRPValue": MRPs,
                                # "Rate" : round(Rate,2),
                                "Rate" : Rate
                            })
                            unique_MRPs.add(MRPs)     
                        
                    # for d in MRPdata:
                    #     CalculatedRateusingMRPMargin=RateCalculationFunction(0,Item,CustomerID,0,1,0,0,d['MRP']).RateWithGST()
                    #     Rate=CalculatedRateusingMRPMargin[0]["NoRatewithOutGST"]
                    #     ItemMRPDetails.append({
                    #     "MRP": d['id'],
                    #     "MRPValue": d['MRP'],   
                    #     "Rate" : round(Rate,2),
                    # })

                # GSTquery = M_GSTHSNCode.objects.filter(Item_id=Item).order_by('-id')[:3] 
                GSTquery=GSTListFun(Item,CustomerID,0)
                if GSTquery.exists():
                    # Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                    ItemGSTDetails = list()
                    for e in GSTquery:
                        ItemGSTDetails.append({
                        "GST": e['id'],
                        "GSTPercentage": e['GSTPercentage'],   
                    }) 

                obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=CustomerID,BaseUnitQuantity__gt=0,IsDamagePieces=0)
                if obatchwisestockquery == "":
                    StockQtySerialize_data =[]
                else:
                    StockQtySerialize_data = StockQtyserializerForPurchaseReturn(obatchwisestockquery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': StockQtySerialize_data})
                    StockDatalist = list()
                    
                    for ad in StockQtySerialize_data:
                        # Rate=RateCalculationFunction(ad['LiveBatche']['id'],ad['Item']['id'],CustomerID,0,1,0,0).RateWithGST()
                        with connection.cursor() as cursor:
                            cursor.execute(f'''
                                SELECT ROUND(RateCalculationFunction1({ad['LiveBatche']['id']}, {ad['Item']['id']}, {CustomerID}, 0, 1, 0, 0,0), 2) AS RateWithoutGST
                            ''')
                            row = cursor.fetchone()
                        Rate = row[0] if row else 0.00

                        # CustomPrint(Rate)

                        if(ad['LiveBatche']['MRP']['id'] is None):
                            MRPValue=ad['LiveBatche']['MRPValue']
                        else:
                            MRPValue=ad['LiveBatche']['MRP']['MRP']
                        
                        if(ad['LiveBatche']['GST']['id'] is None):
                            GSTPercentage=ad['LiveBatche']['GSTPercentage']
                        else:
                            GSTPercentage=ad['LiveBatche']['GST']['GSTPercentage']
                        
                        QtyInNo=UnitwiseQuantityConversion(ad['Item']['id'],ad['BaseUnitQuantity'],0,0,0,1,0).ConvertintoSelectedUnit()
                        
                        StockDatalist.append({
                            "id": ad['id'],
                            "Item":ad['Item']['id'],
                            "BatchDate":ad['LiveBatche']['BatchDate'],
                            "BatchCode":ad['LiveBatche']['BatchCode'],
                            "SystemBatchDate":ad['LiveBatche']['SystemBatchDate'],
                            "SystemBatchCode":ad['LiveBatche']['SystemBatchCode'],
                            "LiveBatche" : ad['LiveBatche']['id'],
                            "LiveBatcheMRPID" : ad['LiveBatche']['MRP']['id'],
                            "LiveBatcheGSTID" : ad['LiveBatche']['GST']['id'],
                            "Rate": round(Rate if Rate is not None else 0.00, 2),
                            "MRP" : MRPValue,
                            "GST" : GSTPercentage,
                            "BaseUnitQuantity":QtyInNo,
                            })

                if BatchCode != "":

                    query = TC_GRNItems.objects.filter(Item=ItemID,BatchCode=BatchCode).order_by('id')[:1]                    
                    if query:
                        GRNItemsdata = TC_GRNItemsSerializerSecond(query, many=True).data
                        # Rate=RateCalculationFunction(0,Itemquery[0]["id"],CustomerID,0,1,0,0).RateWithGST()
                        with connection.cursor() as cursor:
                            cursor.execute(f'''
                                SELECT ROUND(RateCalculationFunction1(0, {Itemquery[0]["id"]}, {CustomerID}, 0, 1, 0, 0,0), 2) AS RateWithoutGST
                            ''')
                            row = cursor.fetchone()
                        Rate = row[0] if row else 0.00

                        for a in GRNItemsdata:
                            MRP = a['MRP']["id"]
                            MRPValue= a['MRPValue']
                            Rate = round(float(Rate if Rate is not None else 0.00), 2)
                            GST= a['GST']["id"]
                            GSTPercentage= a['GSTPercentage']
                            BatchCode= a['BatchCode']
                            BatchDate= a['BatchDate']
                            Unit = Unitquery[0]["id"]
                            UnitName = Unitquery[0]["UnitID__Name"]
                    else:  
                        log_entry = create_transaction_logNew(request, PurchaseReturndata, 0, 'BatchCode is Not Available',57,0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message' : 'Batch Code is Not Available', 'Data': []})      

                else: 
                    
                                 
                        
                        MRP = ""
                        MRPValue= ""                                                
                        GST= ""
                        GSTPercentage= ""
                        BatchCode= ""
                        BatchDate= ""
                        Unit = Unitquery[0]["id"]
                        UnitName = Unitquery[0]["UnitID__Name"]
                       


                
                GRMItem={
                        "Item": Itemquery[0]["id"],
                        "ItemName": Itemquery[0]["Name"],
                        "MRP": MRP,
                        "MRPValue": MRPValue,
                        "Rate": Rate,                
                        "GST": GST,
                        "GSTPercentage": GSTPercentage,
                        "BatchCode": BatchCode,
                        "BatchDate": BatchDate,
                        "Unit" : Unitquery[0]["id"],
                        "UnitName" : Unitquery[0]["UnitID__Name"],                        
                        # "ItemUnitDetails": ItemUnitDetails, 
                        "ItemMRPDetails":ItemMRPDetails,
                        "ItemGSTDetails":ItemGSTDetails,
                        "StockDetails":StockDatalist                         
                }                 

                GRMItems = list()
                GRMItems.append(GRMItem)                  
                log_entry = create_transaction_logNew(request, PurchaseReturndata,0,'',58,0,0,0,CustomerID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRMItems})
        except M_Items.DoesNotExist:
            log_entry = create_transaction_logNew(request, PurchaseReturndata, 0, 'ReturnItemBatchCode Not Available',58,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'ReturnItemBatchCode:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})      


class SalesReturnconsolidatePurchaseReturnView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                ReturnItemdata = JSONParser().parse(request)
                Party= ReturnItemdata['PartyID']
                ReturnID= ReturnItemdata['ReturnID']
                a=ReturnID.split(',')
                Query = TC_PurchaseReturnItems.objects.filter(PurchaseReturn__id__in=a)
                if Query.exists():
                    PurchaseReturnSerializer = PurchaseReturnItemsSerializer2(Query, many=True).data 
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PurchaseReturnSerializer})
                    # PuchaseReturnList=list()
                    PurchaseReturnItemList=list()
                    for b in PurchaseReturnSerializer:
                        #  Rate=RateCalculationFunction(0,b['Item']['id'],Party,0,1,0,0,b['MRPValue']).RateWithGST()
                        Rate =  M_Items.objects.raw(f'''select 1 as id, FoodERP.RateCalculationFunction1(0, {b['Item']['id']}, {Party}, 1, 0, 0, {b['MRPValue']}, 0)Rate''')
                        Imagequery = TC_PurchaseReturnItemImages.objects.filter(PurchaseReturnItem_id=b['id'])
                        # CustomPrint(query.query)
                        ReturnItemImages = list()
                        if Imagequery.exists():
                            ReturnImagesdata = PurchaseReturnItemImageSerializer2(Imagequery, many=True).data
                            
                            
                            for c in ReturnImagesdata:
                                ReturnItemImages.append({
                                "Image": c['Image'],
                            })
                        
                        PurchaseReturnItemList.append({
                            "ItemComment":b['ItemComment'],
                            "Quantity":b['Quantity'],
                            "ApprovedQuantity" : b["ApprovedQuantity"],
                            "BaseUnitQuantity":b['BaseUnitQuantity'],
                            "MRPValue":b['MRPValue'],
                            "Rate":round(float(Rate[0].Rate),2),
                            "BasicAmount":b['BasicAmount'],
                            "TaxType":b['TaxType'],
                            "GSTPercentage":b['GSTPercentage'],
                            "GSTAmount":b['GSTAmount'],
                            "Amount":b['Amount'],
                            "CGST":b['CGST'],
                            "SGST":b['SGST'],
                            "IGST":b['IGST'],
                            "CGSTPercentage":b['CGSTPercentage'],
                            "SGSTPercentage":b['SGSTPercentage'],
                            "IGSTPercentage":b['IGSTPercentage'],
                            "BatchDate":b['BatchDate'],
                            "BatchCode":b['BatchCode'],
                            "CreatedOn":b['CreatedOn'],
                            "GST":b['GST'],
                            "Item" : b["Item"]["id"],
                            "ItemName":b['Item']['Name'],
                            "MRP":b['MRP'],
                            "PurchaseReturn":b['PurchaseReturn'],
                            "Unit":b['Unit']["id"],
                            "UnitName" : b["Unit"]["UnitID"]["Name"],
                            "ItemReason":b['ItemReason']['id'],
                            "ItemReasonName":b['ItemReason']['Name'],
                            "Comment":b['Comment'],
                            "DiscountType":b['DiscountType'],
                            "Discount":b['Discount'],
                            "DiscountAmount":b['DiscountAmount'],
                            "primarySourceID" : b['primarySourceID'],
                            "ApprovedByCompany" : b['ApprovedByCompany'],
                            "ReturnItemImages":ReturnItemImages
                            
                            
                        })
                    log_entry = create_transaction_logNew(request, ReturnItemdata, Party,'Supplier:'+str(Party),59,0)   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PurchaseReturnItemList})
                log_entry = create_transaction_logNew(request, ReturnItemdata, Party, 'PurchaseReturnItemList not available',59,0 )
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'SalesReturnconsolidateItem:'+str(e),33,0 )
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})     
        

class SalesReturnItemApproveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                
                PurchaseReturndata = JSONParser().parse(request)
                ReturnID = PurchaseReturndata['ReturnID']
                CreatedBy = PurchaseReturndata['UserID']  
                IsApprovedflag= PurchaseReturndata['IsApproved'] 
                ReturnItem = PurchaseReturndata['ReturnItem']
                # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':'', 'Data':PurchaseReturndata})
                aa=T_PurchaseReturn.objects.filter(id=ReturnID).update(IsApproved=IsApprovedflag)
                Partyquery = T_PurchaseReturn.objects.filter(id=ReturnID).values('Party')
                Party = Partyquery[0]["Party"]
                item = ""
                query = T_PurchaseReturn.objects.filter(Party_id=Party).values('id')
               
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
               
                for a in ReturnItem:
                    O_BatchWiseLiveStockList=list()     
                    SetFlag=TC_PurchaseReturnItems.objects.filter(id=a["id"]).update(ApprovedQuantity=a["ApprovedQuantity"],ApprovedBy=a["Approvedby"],ApproveComment=a["ApproveComment"])
                    
                    # Company Division Pricelist not assign we got error
                    # Rate=RateCalculationFunction(0,a['Item'],Party,0,1,0,0).RateWithGST()
                    
                    Rate =0.00
                    

                    SaleableItemReason=MC_SettingsDetails.objects.filter(SettingID=14).values('Value')
                    value_str = SaleableItemReason[0]['Value']
                    # Split the string by ',' and convert the resulting substrings to integers
                    values_to_check = [int(val) for val in value_str.split(',')]
                    if a['ItemReason'] in values_to_check:
                        IsDamagePieces =False
                    else:
                        IsDamagePieces =True 
                    
                    query1 = TC_PurchaseReturnItems.objects.filter(Item_id=a['Item'], BatchDate=date.today(), PurchaseReturn_id__in=query).values('id')
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                   
                    if(item == ""):
                        item = a['Item']
                        b = query1.count()

                    elif(item == a['Item']):
                        item = 1
                        b = b+1
                    else:
                        item = a['Item']
                        b = 0
                        
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'],Party, b)
                  
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a["ApprovedQuantity"],0,0,0,1,0)
                   
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                  
                   
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = BaseUnitQuantity
                    
                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Party,
                    "IsDamagePieces":IsDamagePieces,
                    "PurchaseReturn":ReturnID,
                    "CreatedBy":CreatedBy
                    
                    })
                    
                    
                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "MRPValue": a['MRPValue'],

                    "Rate": Rate,                  #'''round(float(Rate[0]["NoRatewithOutGST"]),2)'''

                    "GST": a['GST'],
                    "GSTPercentage": a['GSTPercentage'],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList            
                    
                    })
                   
                PurchaseReturndata.update({"O_LiveBatchesList":O_LiveBatchesList})
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Item Approve Successfully','Data':PurchaseReturndata})
                PurchaseReturn_Serializer = ReturnApproveQtySerializer(data=PurchaseReturndata)
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn_Serializer.save()
                    log_entry = create_transaction_logNew(request, PurchaseReturndata, 0, 'ReturnID:'+str(ReturnID),60,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Item Approve Successfully','Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, PurchaseReturndata, 0,'ReturnItemApprove:'+str(PurchaseReturn_Serializer.errors),34,0 )
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'ReturnItemApprove:'+str(e),33,0 )
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})     
                
                
                
class PurchaseReturnPrintView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Query = T_PurchaseReturn.objects.filter(id=id)
                if Query.exists():
                    PurchaseReturnSerializer = PurchaseReturnPrintSerilaizer(Query, many=True).data 
                    PuchaseReturnList=list()
                    for a in PurchaseReturnSerializer:
                        PurchaseReturnItemList=list()
                    
                        DefCustomerAddress = ''  
                        for ad in a['Customer']['PartyAddress']:
                            if ad['IsDefault'] == True :
                                DefCustomerAddress = ad['Address']
                                
                        DefPartyAddress = ''
                        for x in a['Party']['PartyAddress']:
                            if x['IsDefault'] == True :
                                DefPartyAddress = x['Address']
                        
                        for b in a['ReturnItems']:
                            PurchaseReturnItemList.append({
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'],
                                "ItemComment":b['ItemComment'],
                                "HSNCode":b['GST']['HSNCode'],
                                "Quantity":b['Quantity'],
                                "BaseUnitQuantity":b['BaseUnitQuantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRPValue'],
                                "Rate":b['Rate'],
                                "BasicAmount":b['BasicAmount'],
                                "TaxType":b['TaxType'],
                                "GSTPercentage":b['GSTPercentage'],
                                "GSTAmount":b['GSTAmount'],
                                "Amount":b['Amount'],
                                "CGST":b['CGST'],
                                "SGST":b['SGST'],
                                "IGST":b['IGST'],
                                "CGSTPercentage":b['CGSTPercentage'],
                                "SGSTPercentage":b['SGSTPercentage'],
                                "IGSTPercentage":b['IGSTPercentage'],
                                "BatchDate":b['BatchDate'],
                                "BatchCode":b['BatchCode'],
                                "CreatedOn":b['CreatedOn'],
                                "PurchaseReturn":b['PurchaseReturn'],
                                "Unit":b['Unit']['id'],
                                "UnitName" : b['Unit']['UnitID']['Name'],
                                "ItemReasonID":b['ItemReason']['id'],
                                "ItemReason":b['ItemReason']['Name'],
                                "Comment":b['Comment'],
                                "DiscountType":b['DiscountType'],
                                "Discount":b['Discount'],
                                "DiscountAmount":b['DiscountAmount']
                            })
                
                        PuchaseReturnList.append({
                            "ReturnDate":a['ReturnDate'],
                            "ReturnNo":a['ReturnNo'],
                            "FullReturnNumber":a['FullReturnNumber'],
                            "GrandTotal":a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Comment":a['Comment'],
                            "CreatedOn":a['CreatedOn'],
                            "UpdatedOn":a['UpdatedOn'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "CustomerMobileNo": a['Customer']['MobileNo'],
                            "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
                            "CustomerState": a['Customer']['State']['Name'],     
                            "CustomerAddress": DefCustomerAddress,
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "PartyMobileNo": a['Party']['MobileNo'],
                            "PartyFSSAINo": a['Party']['PartyAddress'][0]['FSSAINo'],
                            "PartyState": a['Party']['State']['Name'],
                            "PartyAddress": DefPartyAddress,       
                            "ReturnReason":a['ReturnReason'],
                            "IsApproved" : a["IsApproved"],
                            "ReturnItems":PurchaseReturnItemList
                            
                        })
                        log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, a['Party']['id'], '',61,0,0,0,a['Customer']['id'])
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PuchaseReturnList[0]})
                log_entry = create_transaction_logNew(request, {'PurchaseReturnID':id}, a['Party']['id'], 'PurchaseReturnPrint not available',61,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'PurchaseReturnPrint:'+str(Exception(e)),33,0 )
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})      


class ReturnImageUpdate(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = [MultiPartParser]
    
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Imagedata = request.data
                '''Image Upload Code End''' 
                avatar = request.FILES.getlist('ASMApprovalImgUpload')
                for file in avatar:
                    Imagedata['ASMApprovalImgUpload']=file
                '''Image Upload Code End'''
                ImageByID = T_PurchaseReturn.objects.get(id=id)
                Image_serializer = ImageSerializer(
                    ImageByID, data=Imagedata)
                if Image_serializer.is_valid():
                    Image_serializer.save()
                    log_entry = create_transaction_logNew(request, Imagedata,0,'ReturnImageID:'+str(id),326,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ReturnImage Upload Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, Imagedata,0,'ReturnImageEdit:'+str(Image_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Image_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'ReturnImagedata:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
        
        

    
          