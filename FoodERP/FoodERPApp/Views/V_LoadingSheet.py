import decimal
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_LoadingSheet import *
from ..Serializer.S_Invoices import *
from ..Serializer.S_BankMaster import *
from ..models import *
from django.db.models import *
from ..Views.V_TransactionNumberfun import GetMaxNumber

class LoadingSheetListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Loadingsheetdata = JSONParser().parse(request)
                FromDate = Loadingsheetdata['FromDate']
                ToDate = Loadingsheetdata['ToDate']
                Party = Loadingsheetdata['PartyID']
                query = T_LoadingSheet.objects.filter(Date__range=[FromDate, ToDate], Party=Party)
                if query.exists():
                    LoadingSheet_Serializer = LoadingSheetListSerializer(query, many=True).data
                    LoadingSheetListData = list()
                    for a in LoadingSheet_Serializer:
                        RouteID = a['Route']
                        Route_list = RouteID.split(",")
                        query = M_Routes.objects.filter(id__in=Route_list).values('Name')
                        routelist = ''
                        for b in query:
                            routelist = routelist+ b['Name'] + ','
                            
                        LoadingSheetListData.append({
                            "id": a['id'],
                            "Date": a['Date'],
                            "LoadingSheetNo": a['No'],
                            "RouteName": routelist[:-1],
                            "TotalAmount": a['TotalAmount'],
                            "InvoiceCount": a['InvoiceCount'],
                            "VehicleNo": a['Vehicle']['VehicleNumber'],
                            "VehicleType": a['Vehicle']['VehicleType']['Name'],
                            "DriverName": a['Driver']['Name'],
                            "CreatedOn" :a['CreatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': LoadingSheetListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Not available', 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



class LoadingSheetView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Loadingsheetdata = JSONParser().parse(request)
                Party = Loadingsheetdata['Party']
                Date = Loadingsheetdata['Date']
                a = GetMaxNumber.GetLoadingSheetNumber(Party,Date)
                Loadingsheetdata['No'] = str(a)
                Loadingsheet_Serializer = LoadingSheetSerializer(data=Loadingsheetdata)
                if Loadingsheet_Serializer.is_valid():
                    Loadingsheet_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Loadingsheet_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = T_LoadingSheet.objects.filter(id=id)
                LoadingSheet_Serializer = LoadingSheetListSerializer(query, many=True).data
                InvoiceData = list()
                LoadingSheetListData = list()
                for a in LoadingSheet_Serializer:
                    
                    RouteID = a['Route']
                    Route_list = RouteID.split(",")
                    query = M_Routes.objects.filter(id__in=Route_list).values('Name')
                    routelist = ''
                    for b in query:
                        routelist = routelist+ b['Name'] + ','
                    
                    LoadingSheetListData.append({
                        "id": a['id'],
                        "Date": a['Date'],
                        "Party":a['Party']['Name'],
                        "PartyAddress":a['Party']['PartyAddress'][0]['Address'],
                        "LoadingSheetNo": a['No'],
                        "RouteName":  routelist[:-1],
                        "TotalAmount": a['TotalAmount'],
                        "InvoiceCount": a['InvoiceCount'],
                        "VehicleNo": a['Vehicle']['VehicleNumber'],
                        "VehicleType": a['Vehicle']['VehicleType']['Name'],
                        "DriverName": a['Driver']['Name'],
                        "CreatedOn" : a['CreatedOn']
                    })
                q1 = TC_LoadingSheetDetails.objects.filter(LoadingSheet=id).values('Invoice') 
                InvoiceQuery = T_Invoices.objects.filter(id__in=q1)
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    InvoiceParent = list()
                    for a in InvoiceSerializedata:
                        Amount = TC_ReceiptInvoices.objects.filter(Invoice=a['id']).aggregate(PAmount=Sum('PaidAmount'))
                        if Amount['PAmount'] is None:
                            PaidAmount = 0.000
                        else:
                            PaidAmount = Amount['PAmount']
                        
                        if float(PaidAmount) != float(a['GrandTotal']):
                            Flag = False
                        else:
                            Flag = True
                                
                        InvoiceParent.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "InvoiceNumber": a['InvoiceNumber'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "ReceiptFlag": Flag
                        })
                    InvoiceData.append({
                        "PartyDetails":LoadingSheetListData[0],
                        "InvoiceParent":InvoiceParent,
                    })    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0] })
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Loadingsheetdata = JSONParser().parse(request)
                LoadingsheetdataByID = T_LoadingSheet.objects.get(id=id)
                Loadingsheet_Serializer = LoadingSheetSerializer(LoadingsheetdataByID, data=Loadingsheetdata)
                if Loadingsheet_Serializer.is_valid():
                    Loadingsheet_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Loadingsheet_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Loadingsheetdata = T_LoadingSheet.objects.get(id=id)
                Loadingsheetdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Deleted Successfully', 'Data':[]})
        except T_LoadingSheet.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Loading Sheet Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Loading Sheet used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
  
class LoadingSheetInvoicesView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                FromDate = Invoicedata['FromDate']
                ToDate = Invoicedata['ToDate']
                Party = Invoicedata['Party']
                Route = Invoicedata['Route']
                Route_list = Route.split(",")
              
                if(Route == ''):
                    query =  T_Invoices.objects.raw('''SELECT T_Invoices.id as id, T_Invoices.InvoiceDate, T_Invoices.Customer_id, T_Invoices.FullInvoiceNumber, T_Invoices.GrandTotal, T_Invoices.Party_id, T_Invoices.CreatedOn,  T_Invoices.UpdatedOn, M_Parties.Name FROM T_Invoices join M_Parties on  M_Parties.id=  T_Invoices.Customer_id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Party_id = %s AND T_Invoices.id Not in(SELECT  Invoice_id From TC_LoadingSheetDetails) ''',[FromDate,ToDate,Party])
                else:
                    query =  T_Invoices.objects.raw('''SELECT T_Invoices.id as id, T_Invoices.InvoiceDate, T_Invoices.Customer_id, T_Invoices.FullInvoiceNumber, T_Invoices.GrandTotal, T_Invoices.Party_id, T_Invoices.CreatedOn, T_Invoices.UpdatedOn,M_Parties.Name FROM T_Invoices join M_Parties on M_Parties.id=  T_Invoices.Customer_id join MC_PartySubParty on MC_PartySubParty.SubParty_id = T_Invoices.Customer_id  WHERE  MC_PartySubParty.Route_id IN %s AND T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Party_id=%s AND T_Invoices.id Not in(SELECT  Invoice_id From TC_LoadingSheetDetails) ''', [Route_list,FromDate,ToDate,Party])
                if query:
                    Invoice_serializer = LoadingSheetInvoicesSerializer(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Invoice_serializer})
                    InvoiceListData = list()
                    for a in Invoice_serializer:
                        InvoiceListData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "Customer": a['Name'],
                            "CustomerID": a['Customer_id'],
                            "PartyID": a['Party_id'],
                            "GrandTotal": a['GrandTotal'],
                            "CreatedOn": a['CreatedOn'] 
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

######################################## Loading Sheet Print API ##################################################

class LoadingSheetPrintView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = T_LoadingSheet.objects.filter(id=id)
                LoadingSheet_Serializer = LoadingSheetListSerializer(query, many=True).data
                InvoiceData = list()
                LoadingSheetListData = list()
                for a in LoadingSheet_Serializer:
                    
                    RouteID = a['Route']
                    Route_list = RouteID.split(",")
                    query = M_Routes.objects.filter(id__in=Route_list).values('Name')
                    routelist = ''
                    for b in query:
                        routelist = routelist+ b['Name'] + ','
                    
                    LoadingSheetListData.append({
                        "id": a['id'],
                        "Date": a['Date'],
                        "Party":a['Party']['Name'],
                        "PartyAddress":a['Party']['PartyAddress'][0]['Address'],
                        "LoadingSheetNo": a['No'],
                        "RouteName":  routelist[:-1],
                        "TotalAmount": a['TotalAmount'],
                        "InvoiceCount": a['InvoiceCount'],
                        "VehicleNo": a['Vehicle']['VehicleNumber'],
                        "VehicleType": a['Vehicle']['VehicleType']['Name'],
                        "DriverName": a['Driver']['Name'],
                        "CreatedOn" : a['CreatedOn']
                    })
                q1 = TC_LoadingSheetDetails.objects.filter(LoadingSheet=id).values('Invoice') 
                InvoiceQuery = T_Invoices.objects.filter(id__in=q1)
                
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0] })
                    InvoiceParent = list()
                    for b in InvoiceSerializedata:
                        InvoiceParent.append({
                            "id": b['id'],
                            "InvoiceDate": b['InvoiceDate'],
                            "InvoiceNumber": b['InvoiceNumber'],
                            "FullInvoiceNumber": b['FullInvoiceNumber'],
                            "TCSAmount" : b["TCSAmount"],
                            "GrandTotal": b['GrandTotal'],
                            "RoundOffAmount":b['RoundOffAmount'],
                            "Customer": b['Customer']['id'],
                            "CustomerName": b['Customer']['Name'],
                            "CustomerGSTIN": b['Customer']['GSTIN'],
                            "Party": b['Party']['id'],
                            "PartyName": b['Party']['Name'],
                            "PartyGSTIN": b['Party']['GSTIN'],
                        })
                    
                    Invoicelist = list()
                    InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    for x in InvoiceSerializedata:
                        Invoicelist.append(x['id'])
                    InvoiceItemDetails = list()        
                    Itemsquery =TC_InvoiceItems.objects.raw('''SELECT TC_InvoiceItems.id,TC_InvoiceItems.Item_id,TC_InvoiceItems.Unit_id,M_Items.Name ItemName, SUM(Quantity)Quantity,MRPValue, SUM(Amount) Amount, BatchCode, SUM(QtyInBox)QtyInBox,SUM(QtyInNo)QtyInNo 
                    ,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName
                    FROM TC_InvoiceItems 
                    JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id 
                    JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id 
                    JOIN M_Units ON M_Units.id =MC_ItemUnits.UnitID_id
                    left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
                    left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
                    left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                    left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
                    WHERE TC_InvoiceItems.Invoice_id IN %s group by TC_InvoiceItems.Item_id, TC_InvoiceItems.MRP_id Order By M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence ''',[Invoicelist])    
                    
                    InvoiceItemSerializedata = LoadingSheetPrintSerializer(Itemsquery, many=True).data
                    for c in InvoiceItemSerializedata:
                        
                        # Box Qty and Pieces Qty 
                        
                        MCItemUnit= MC_ItemUnits.objects.all().filter(Item=c['Item_id'],IsDeleted=0,UnitID=4).values('id')
                     
                        if MCItemUnit:
                            QtyInBox = c['QtyInBox']
                            integer_part, decimal_part = QtyInBox.split(".")
                            QtyInNo=UnitwiseQuantityConversion(c['Item_id'],integer_part,MCItemUnit[0]['id'],0,0,1,0).ConvertintoSelectedUnit()
                            PiecesQty = float(c['QtyInNo']) -float(QtyInNo) 
                        else:
                            QtyInBox = c['QtyInBox']
                            integer_part, decimal_part = QtyInBox.split(".")
                            QtyInNo=0.00
                            PiecesQty = float(c['QtyInNo']) -float(QtyInNo)
                        
                        InvoiceItemDetails.append({
                            "id": c['id'],
                            "id": c['Item_id'],
                            "ItemName": c['ItemName'],
                            "GroupTypeName" : c["GroupTypeName"],
                            "GroupName" : c["GroupName"],
                            "SubGroupName" : c["SubGroupName"],
                            "MRPValue": c['MRPValue'],
                            "Amount" : c['Amount'],
                            "BatchCode": c['BatchCode'],
                            "BoxQty": integer_part,
                            "PiecesQty":round(PiecesQty),
                            "QtyInNo": round(float(c['QtyInNo']),2)
                        })
                        
                    InvoiceData.append({
                        "PartyDetails":LoadingSheetListData[0],
                        "InvoiceItems":InvoiceItemDetails,
                        "InvoiceParent":InvoiceParent,
                    })    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0] })
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Loading Sheet Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

######################################## MultipleInvoice Loading Sheet Print API ##################################################
class MultipleInvoicesView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                q1 = TC_LoadingSheetDetails.objects.filter(LoadingSheet=id).values('Invoice') 
                InvoiceIDs = T_Invoices.objects.filter(id__in=q1).values('id')
                InvoiceList = list()
                for InvoiceID in InvoiceIDs:
                    InvoiceQuery = T_Invoices.objects.filter(id=InvoiceID['id'])
                    if InvoiceQuery.exists():
                        InvoiceSerializedata = InvoiceSerializerThird(InvoiceQuery, many=True).data
                        
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
                                    "MRPValue": b['MRP']['MRP'],
                                    "Rate": b['Rate'],
                                    "TaxType": b['TaxType'],
                                    "PrimaryUnitName":b['Unit']['UnitID']['Name'],
                                    "UnitName":bb,
                                    "BaseUnitQuantity": b['BaseUnitQuantity'],
                                    "GST": b['GST']['id'],
                                    "GSTPercentage": b['GST']['GSTPercentage'],
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
                                    "HSNCode":b['GST']['HSNCode'],
                                    "BatchCode": b['BatchCode'],
                                    "BatchDate": b['BatchDate'],
                                    "DiscountType":b['DiscountType'],
                                    "Discount":b['Discount'],
                                    "DiscountAmount":b['DiscountAmount']
                                })
                                
                                InvoiceReferenceDetails = list()
                            for d in a['InvoicesReferences']:
                                InvoiceReferenceDetails.append({
                                    "Invoice": d['Invoice'],
                                    "Order": d['Order']['id'],
                                    "FullOrderNumber": d['Order']['FullOrderNumber'],
                                    "Description":d['Order']['Description']
                                })
                            
                            query= MC_PartyBanks.objects.filter(Party=a['Party']['id'],IsSelfDepositoryBank=1,IsDefault=1).all()
                            BanksSerializer=PartyBanksSerializer(query, many=True).data
                            BankData=list()
                            for e in BanksSerializer:
                                BankData.append({
                                    "BankName": e['BankName'],
                                    "BranchName": e['BranchName'],
                                    "IFSC": e['IFSC'],
                                    "AccountNo": e['AccountNo'],
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
                                "PartyState": a['Party']['State']['Name'],
                                "CustomerState": a['Customer']['State']['Name'],
                                "PartyFSSAINo": a['Party']['PartyAddress'][0]['FSSAINo'],
                                "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
                                "PartyAddress": a['Party']['PartyAddress'],
                                "CustomerAddress": a['Customer']['PartyAddress'],
                                "PartyGSTIN": a['Party']['GSTIN'],
                                "PartyMobileNo": a['Party']['MobileNo'],
                                "CreatedOn" : a['CreatedOn'],
                                "DriverName":a['Driver']['Name'],
                                "VehicleNo": a['Vehicle']['VehicleNumber'],
                                "InvoiceItems": InvoiceItemDetails,
                                "InvoicesReferences": InvoiceReferenceDetails,
                                "InvoiceUploads" : a["InvoiceUploads"],
                                "BankData":BankData
                                
                            })
                    InvoiceList.append( InvoiceData[0] )   
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceList})        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})  