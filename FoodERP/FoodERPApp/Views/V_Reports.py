
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Items import ItemReportSerializer
from SweetPOS.models import *
from ..Serializer.S_Parties import M_PartiesSerializerSecond
from ..Views.V_CommFunction import *
from ..Views.V_CommFunction import GetOpeningBalance, UnitwiseQuantityConversion, RateCalculationFunction
from ..Serializer.S_Invoices import InvoiceSerializerSecond
from collections import defaultdict
from django.db import connection
from ..Serializer.S_Reports import *
from ..models import *
from datetime import datetime, timedelta
from django.db.models import Sum

# Changes by Pratiksha : In ManPowerReport-> a.fssaidocumenturl is just a string path in raw sql query, not a FileField.So if you directly pass it to get_uploaded_filename() as it is now, you’ll getAttributeError: 'str' object has no attribute 'name'
class DummyFile:
    def __init__(self, name):
        self.name = name


class PartyLedgerReportView(CreateAPIView):  
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Party = Orderdata['Party']

                query = T_Invoices.objects.raw('''SELECT
    1 id,InvoiceDate,BillNo,BankName,BranchName,ChequeDate,DocumentNo,ReceiptMode,InvoiceAmount,TotalTCS,
    ReceiptAmt,CashReceiptAmt,DebitNote,CreditNote,Flag,BasicAmount,BA5,BA12,BA18,GA5,GA12,GA18,Description
FROM
    (
        (   
            SELECT InvoiceDate,BillNo,BankName,BranchName,ChequeDate,DocumentNo,ReceiptMode,InvoiceAmount,
            TotalTCS,ReceiptAmt,CashReceiptAmt,Flag,DebitNote,CreditNote,ifnull(BasicAmount,0) AS BasicAmount,
            ifnull(BA5,0) AS BA5,ifnull(BA12,0) AS BA12,ifnull(BA18,0) AS BA18,ifnull(GA5,0) AS GA5,
            ifnull(GA12,0) AS GA12,ifnull(GA18,0) AS GA18,Description
            
            FROM
                (SELECT InvoiceDate,T_Invoices.id,FullInvoiceNumber BillNo,"" AS BankName,"" AS BranchName,
                "" AS ChequeDate,"" AS DocumentNo,"" AS ReceiptMode,GrandTotal InvoiceAmount,TCSAmount TotalTCS,
                0 AS ReceiptAmt,0 AS CashReceiptAmt,1 AS Flag,0 AS DebitNote,0 AS CreditNote,"" AS Description
                FROM T_Invoices WHERE InvoiceDate BETWEEN %s AND %s AND Party_id = %s AND Customer_id = %s) a
                
                LEFT JOIN 
                
                (SELECT Invoice_id,SUM(BasicAmount) AS BasicAmount,
                SUM(CASE WHEN GSTPercentage = 5 THEN BasicAmount ELSE 0 END) AS BA5,
                SUM(CASE WHEN GSTPercentage = 12 THEN BasicAmount ELSE 0 END) AS BA12,
                SUM(CASE WHEN GSTPercentage = 18 THEN BasicAmount ELSE 0 END) AS BA18,
                SUM(CASE WHEN GSTPercentage = 5 THEN GSTAmount ELSE 0 END) AS GA5,
                SUM(CASE WHEN GSTPercentage = 12 THEN GSTAmount ELSE 0 END) AS GA12,
                SUM(CASE WHEN GSTPercentage = 18 THEN GSTAmount ELSE 0 END) AS GA18
                FROM TC_InvoiceItems GROUP BY Invoice_id) b 
            
            ON a.id = b.Invoice_id
        )

        UNION
            SELECT ReceiptDate InvoiceDate,FullReceiptNumber BillNo,M_Bank.Name AS BankName,MC_PartyBanks.BranchName AS BranchName,
            ChequeDate ChequeDate,DocumentNo DocumentNo,M_GeneralMaster.Name AS ReceiptMode,0 AS InvoiceAmount,0 as TotalTCS,
            CASE WHEN ReceiptMode_id = 31 THEN 0 ELSE AmountPaid END ReceiptAmt,
            CASE WHEN ReceiptMode_id = 31 THEN AmountPaid ELSE 0 END CashReceiptAmt,
            2 AS Flag,0 AS DebitNote,0 AS CreditNote,0 AS BasicAmount,0 AS BA5,0 AS BA12,0 AS BA18,0 AS GA5,0 AS GA12,
            0 AS GA18,Description
            FROM T_Receipts
            LEFT JOIN MC_PartyBanks ON MC_PartyBanks.id = T_Receipts.Bank_id
            LEFT JOIN M_Bank ON M_Bank.id = MC_PartyBanks.Bank_id
            INNER JOIN M_GeneralMaster ON M_GeneralMaster.id = T_Receipts.ReceiptMode_id
            WHERE ReceiptDate BETWEEN %s AND %s
            AND T_Receipts.Party_id = %s
            AND T_Receipts.Customer_id = %s

        UNION
            SELECT CRDRNoteDate InvoiceDate,FullNoteNumber BillNo,"" AS BankName,"" AS BranchName,"" AS ChequeDate,
            "" AS DocumentNo,"" AS ReceiptMode,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 or T_CreditDebitNotes.NoteType_id = 40 THEN T_CreditDebitNotes.GrandTotal ELSE 0 END) AS InvoiceAmount,
            0 AS TotalTCS,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 or T_CreditDebitNotes.NoteType_id = 40 THEN 0 ELSE T_CreditDebitNotes.GrandTotal END) ReceiptAmt,
            0 AS CashReceiptAmt,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 or T_CreditDebitNotes.NoteType_id = 40 THEN 3 ELSE 4 END) AS Flag,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38  OR T_CreditDebitNotes.NoteType_id =40 THEN T_CreditDebitNotes.GrandTotal ELSE 0 END) AS DebitNote,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 OR T_CreditDebitNotes.NoteType_id =40 THEN 0 ELSE T_CreditDebitNotes.GrandTotal END) CreditNote,
            0 AS BasicAmount,0 AS BA5, 0 AS BA12, 0 AS BA18, 0 AS GA5, 0 AS GA12, 0 AS GA18, "" AS Description
            FROM T_CreditDebitNotes
            WHERE
             T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND Party_id = %s
            AND Customer_id = %s and IsDeleted=0

        UNION
            SELECT Date InvoiceDate,"" BillNo,"" AS BankName,"" AS BranchName,"" AS ChequeDate,
            "" AS DocumentNo,"" AS ReceiptMode,
            OpeningBalanceAmount AS InvoiceAmount,0 AS TotalTCS,
            0 AS ReceiptAmt,0 AS CashReceiptAmt,
            0 AS Flag,
            0 AS DebitNote,
            0 AS CreditNote,
            0 AS BasicAmount,0 AS BA5, 0 AS BA12, 0 AS BA18, 0 AS GA5, 0 AS GA12, 0 AS GA18, "OpeningBalance" AS Description
            FROM MC_PartySubPartyOpeningBalance
            WHERE
             MC_PartySubPartyOpeningBalance.Date BETWEEN %s AND %s AND Party_id = %s
            AND SubParty_id = %s   

    ) q
            ORDER BY InvoiceDate , Flag , BillNo ''', [FromDate, ToDate, Party, Customer, FromDate, ToDate, Party, Customer, FromDate, ToDate, Party, Customer,FromDate, ToDate, Party, Customer])

                if not query:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'Report Not Found', 206, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    PartyLedgerSerializedata = PartyLedgerReportSerializer(
                        query, many=True).data
                    PartyLedgerData = list()
                    PartyLedgerItemDetails = list()
                    date_format = "%Y-%m-%d"

                    # Convert the string to a date object
                    date_object = datetime.strptime(FromDate, date_format).date()
                    previous_date = date_object - timedelta(days=1)
                    Opening = GetOpeningBalance(Party, Customer, previous_date)
                    Closing = GetOpeningBalance(Party, Customer, ToDate)
                    temp = 0
                    TaxFreeSale = 0
                    TotalTaxableSale = 0
                    TaxableSale5 = 0
                    TaxableSale12 = 0
                    TaxableSale18 = 0
                    GSTAmount5 = 0
                    GSTAmount12 = 0
                    GSTAmount18 = 0
                    TotalCreditNote = 0
                    TotalDebitNote = 0
                    TotalTCS = 0
                    for a in PartyLedgerSerializedata:
                        Openingba=Opening
                        if a['Flag'] == 0 :
                            temp=0
                            Openingba= 0
                        if temp == 0:
                            temp = (float(Openingba) + float(a['InvoiceAmount'])) - (
                                float(a['ReceiptAmt'])+float(a['CashReceiptAmt']))
                        else:
                            temp = (temp + float(a['InvoiceAmount'])) - \
                                (float(a['ReceiptAmt']) +
                                 float(a['CashReceiptAmt']))

                        TaxFreeSale = 0.0
                        TotalTaxableSale = TotalTaxableSale + \
                            float(a["BasicAmount"])
                        TaxableSale5 = TaxableSale5 + float(a["BA5"])
                        TaxableSale12 = TaxableSale12 + float(a["BA12"])
                        TaxableSale18 = TaxableSale18 + float(a["BA18"])
                        GSTAmount5 = GSTAmount5 + float(a["GA5"])
                        GSTAmount12 = GSTAmount12 + float(a["GA12"])
                        GSTAmount18 = GSTAmount18 + float(a["GA18"])
                        TotalCreditNote = TotalCreditNote + \
                            float(a["CreditNote"])
                        TotalDebitNote = TotalDebitNote + float(a["DebitNote"])
                        TotalTCS = TotalTCS + float(a["TotalTCS"])
                        if a['BankName'] is None:
                            BankName = ''
                        else:
                            BankName = str(a['BankName'])
                        if a['BranchName'] is None:
                            BranchName = ''
                        else:
                            BranchName = str(a['BranchName'])
                        if a['DocumentNo'] is None:
                            DocumentNo = ''
                        else:
                            DocumentNo = str(a['DocumentNo'])
                        if a['ReceiptMode'] is None:
                            ReceiptMode = ''
                        else:
                            ReceiptMode = str(a['ReceiptMode'])

                        if a['Description'] is None or not a['Description']:

                            Description = ''
                        else:

                            Description = '(' + str(a['Description']) + ')'

                        PartyLedgerItemDetails.append({
                            "Date": a['InvoiceDate'],
                            "DocumentNO": a['BillNo'],
                            "Particular": BankName+''+BranchName+''+DocumentNo+''+ReceiptMode + '' + Description,
                            "Amount": a['InvoiceAmount'],
                            "RecieptAmount": float(a['ReceiptAmt']) + float(a['CashReceiptAmt']),
                            "Cash": 0,
                            "Balance": float(temp),

                        })
                    q1 = M_Parties.objects.filter(
                        id=Party).values("Name", "PAN", "GSTIN")
                    q2 = M_Parties.objects.filter(
                        id=Customer).values("Name", "PAN", "GSTIN")
                    PartyLedgerData.append({
                        "FormDate": FromDate,
                        "ToDate": ToDate,
                        "Distributor": q1[0]['Name'],
                        "DistributorGSTIN": q1[0]["GSTIN"],
                        "DistributorPAN": q1[0]['PAN'],
                        "CustomerName": q2[0]['Name'],
                        "CustomerGSTIN":  q2[0]["GSTIN"],
                        "CustomerPAN": q2[0]["PAN"],
                        "Open": Opening,
                        "Close": Closing,
                        "TaxFreeSale": TaxFreeSale,
                        "TotalTaxableSale": TotalTaxableSale,
                        "TaxableSale5": TaxableSale5,
                        "TaxableSale12": TaxableSale12,
                        "TaxableSale18": TaxableSale18,
                        "GSTAmount5": GSTAmount5,
                        "GSTAmount12": GSTAmount12,
                        "GSTAmount18": GSTAmount18,
                        "TotalCreditNote": TotalCreditNote,
                        "TotalDebitNote": TotalDebitNote,
                        "TotalTCS": TotalTCS,
                        "InvoiceItems": PartyLedgerItemDetails
                    })
                log_entry = create_transaction_logNew(request, Orderdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 206, 0, FromDate, ToDate, Customer)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyLedgerData})
        except Exception as e:
            log_entry = create_transaction_logNew( request, Orderdata, 0, 'PartyLedgerReport'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class GenericSaleView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Genericdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Genericdata['FromDate']
                ToDate = Genericdata['ToDate']
                Party = Genericdata['Party']
                Party_list = Party.split(",")
                
                party_types = M_Parties.objects.filter(id__in=Party_list).values('id', 'PartyType_id')
                
                franchise_parties = []
                other_parties = []
                Final_Data = []
                
                for party in party_types:
                    if party['PartyType_id'] == 19:
                        franchise_parties.append(party['id'])
                    else:
                        other_parties.append(party['id'])   
                
                party_tuple_franchise_parties = tuple(franchise_parties) if franchise_parties else (0,)
                party_tuple_other_parties = tuple(other_parties) if other_parties else (0,)
                
                if party_tuple_other_parties:
                    
                    query ='''SELECT TC_InvoiceItems.id, A.SAPPartyCode SAPPartyID, T_Invoices.Party_id AS PartyID,A.Name PartyName, X.Name PartyType, T_Invoices.ImportFromExcel,  T_Invoices.FullInvoiceNumber,
T_Invoices.InvoiceDate,T_Invoices.Customer_id AS CustomerID,B.Name CustomerName, Y.Name CustomeType, M_Drivers.Name DriverName,
M_Vehicles.VehicleNumber VehicleNo,TC_InvoiceItems.Item_id AS ItemID,M_Items.Name ItemName,C_Companies.Name CompanyName,
M_GSTHSNCode.HSNCode,TC_InvoiceItems.MRPValue AS MRP,ROUND(TC_InvoiceItems.QtyInNo, 2) AS QtyInNo,ROUND(TC_InvoiceItems.QtyInKg, 2) AS QtyInKg,ROUND(TC_InvoiceItems.QtyInBox, 2) AS QtyInBox,
TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate + ((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage) / 100)) WithGSTRate,
M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType,TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,
TC_InvoiceItems.BasicAmount AS TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,
TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,TC_InvoiceItems.GSTPercentage,
TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Orders.FullOrderNumber,T_Orders.OrderDate,T_Invoices.TCSAmount,
T_Invoices.RoundOffAmount,T_Invoices.GrandTotal,M_Group.Name AS `Group`, MC_SubGroup.Name AS SubGroup, T_Invoices.CreatedOn,
M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster, TC_InvoiceItems.BatchCode AS BatchNo , TC_InvoiceItems.BatchDate,
M_Items.SAPItemCode SAPItemID ,'' VoucherCode,'' CashierName, FoodERP.M_PriceList.Name AS PriceListName
FROM FoodERP.TC_InvoiceItems 
JOIN FoodERP.T_Invoices ON FoodERP.T_Invoices.id = FoodERP.TC_InvoiceItems.Invoice_id 
JOIN FoodERP.MC_PartySubParty ON FoodERP.MC_PartySubParty.SubParty_id = FoodERP.T_Invoices.Customer_id and MC_PartySubParty.Party_id=T_Invoices.Party_id
left JOIN FoodERP.TC_InvoicesReferences ON FoodERP.TC_InvoicesReferences.Invoice_id = FoodERP.T_Invoices.id 
left JOIN FoodERP.T_Orders ON FoodERP.T_Orders.id = FoodERP.TC_InvoicesReferences.Order_id
JOIN FoodERP.M_Parties A ON A.id = FoodERP.T_Invoices.Party_id 
JOIN FoodERP.M_Parties B ON B.id = FoodERP.T_Invoices.Customer_id 
LEFT JOIN FoodERP.M_PriceList ON M_PriceList.id = B.PriceList_id 
JOIN FoodERP.M_PartyType X on A.PartyType_id = X.id 
JOIN FoodERP.M_PartyType Y on B.PartyType_id = Y.id 
JOIN FoodERP.M_Items ON M_Items.id = FoodERP.TC_InvoiceItems.Item_id 
JOIN FoodERP.C_Companies ON FoodERP.C_Companies.id = FoodERP.M_Items.Company_id 
left JOIN FoodERP.M_GSTHSNCode ON FoodERP.M_GSTHSNCode.id = FoodERP.TC_InvoiceItems.GST_id 
JOIN FoodERP.MC_ItemUnits ON FoodERP.MC_ItemUnits.id = FoodERP.TC_InvoiceItems.Unit_id 
JOIN FoodERP.M_Units ON FoodERP.M_Units.id = FoodERP.MC_ItemUnits.UnitID_id 
LEFT JOIN FoodERP.M_Drivers ON FoodERP.M_Drivers.id = T_Invoices.Driver_id 
LEFT JOIN FoodERP.M_Vehicles ON FoodERP.M_Vehicles.id = T_Invoices.Vehicle_id 
left JOIN FoodERP.MC_ItemGroupDetails ON FoodERP.MC_ItemGroupDetails.Item_id = FoodERP.M_Items.id  and FoodERP.MC_ItemGroupDetails.GroupType_id=1
LEFT JOIN FoodERP.M_Group ON M_Group.id  = FoodERP.MC_ItemGroupDetails.Group_id 
LEFT JOIN FoodERP.MC_SubGroup ON FoodERP.MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
LEFT JOIN FoodERP.M_PartyDetails on  A.id=FoodERP.M_PartyDetails.Party_id AND FoodERP.M_PartyDetails.Group_id is null
LEFT JOIN FoodERP.M_Cluster On FoodERP.M_PartyDetails.Cluster_id=FoodERP.M_Cluster.id 
LEFT JOIN FoodERP.M_SubCluster on FoodERP.M_PartyDetails.SubCluster_id=FoodERP.M_SubCluster.Id 
WHERE FoodERP.T_Invoices.InvoiceDate BETWEEN %s AND %s AND FoodERP.T_Invoices.Party_id in %s'''
                    
                    Other_Data = list(T_Invoices.objects.raw(query, [FromDate, ToDate, party_tuple_other_parties]))  
                    Final_Data.extend(Other_Data)
                     
                if party_tuple_franchise_parties:
                    
                    
                    # MC_PartySubParty join use madhe nahi so remove kela aahe. 
                    # JOIN FoodERP.MC_PartySubParty ON FoodERP.MC_PartySubParty.SubParty_id = SweetPOS.T_SPOSInvoices.Customer and FoodERP.MC_PartySubParty.Party_id=SweetPOS.T_SPOSInvoices.Party
                    query = '''SELECT SweetPOS.TC_SPOSInvoiceItems.ClientID,SweetPOS.TC_SPOSInvoiceItems.id, A.SAPPartyCode SAPPartyID, SweetPOS.T_SPOSInvoices.Party AS PartyID,A.Name PartyName, X.Name PartyType, '' ImportFromExcel,  SweetPOS.T_SPOSInvoices.FullInvoiceNumber,
SweetPOS.T_SPOSInvoices.InvoiceDate,SweetPOS.T_SPOSInvoices.Customer AS CustomerID,B.Name CustomerName, Y.Name CustomeType, M_Drivers.Name DriverName,
M_Vehicles.VehicleNumber VehicleNo,SweetPOS.TC_SPOSInvoiceItems.Item AS ItemID,M_Items.Name ItemName,C_Companies.Name CompanyName,
SweetPOS.TC_SPOSInvoiceItems.HSNCode,SweetPOS.TC_SPOSInvoiceItems.MRPValue AS MRP,ROUND(SweetPOS.TC_SPOSInvoiceItems.QtyInNo, 2) AS QtyInNo,ROUND(SweetPOS.TC_SPOSInvoiceItems.QtyInKg, 2) AS QtyInKg,
ROUND(SweetPOS.TC_SPOSInvoiceItems.QtyInBox, 2) AS QtyInBox,
SweetPOS.TC_SPOSInvoiceItems.Rate AS BasicRate,(SweetPOS.TC_SPOSInvoiceItems.Rate + ((SweetPOS.TC_SPOSInvoiceItems.Rate * SweetPOS.TC_SPOSInvoiceItems.GSTPercentage) / 100)) WithGSTRate,
M_Units.Name AS UnitName,SweetPOS.TC_SPOSInvoiceItems.DiscountType,SweetPOS.TC_SPOSInvoiceItems.Discount,SweetPOS.TC_SPOSInvoiceItems.DiscountAmount,
SweetPOS.TC_SPOSInvoiceItems.BasicAmount AS TaxableValue,SweetPOS.TC_SPOSInvoiceItems.CGST,SweetPOS.TC_SPOSInvoiceItems.CGSTPercentage,SweetPOS.TC_SPOSInvoiceItems.SGST,
SweetPOS.TC_SPOSInvoiceItems.SGSTPercentage,SweetPOS.TC_SPOSInvoiceItems.IGST,SweetPOS.TC_SPOSInvoiceItems.IGSTPercentage,SweetPOS.TC_SPOSInvoiceItems.GSTPercentage,
SweetPOS.TC_SPOSInvoiceItems.GSTAmount,SweetPOS.TC_SPOSInvoiceItems.Amount AS TotalValue,T_Orders.FullOrderNumber,T_Orders.OrderDate,SweetPOS.T_SPOSInvoices.TCSAmount,
SweetPOS.T_SPOSInvoices.RoundOffAmount,SweetPOS.T_SPOSInvoices.GrandTotal,M_Group.Name AS `Group`, MC_SubGroup.Name AS SubGroup, T_SPOSInvoices.CreatedOn,
M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster, SweetPOS.TC_SPOSInvoiceItems.BatchCode AS BatchNo ,
SweetPOS.TC_SPOSInvoiceItems.BatchDate, M_Items.SAPItemCode SAPItemID,
VoucherCode,FoodERP.M_Users.LoginName CashierName, FoodERP.M_PriceList.Name AS PriceListName
FROM SweetPOS.TC_SPOSInvoiceItems
JOIN SweetPOS.T_SPOSInvoices ON SweetPOS.T_SPOSInvoices.id = SweetPOS.TC_SPOSInvoiceItems.Invoice_id
JOIN FoodERP.M_Users ON FoodERP.M_Users.id=SweetPOS.T_SPOSInvoices.CreatedBy
left JOIN SweetPOS.TC_SPOSInvoicesReferences ON SweetPOS.TC_SPOSInvoicesReferences.Invoice_id = SweetPOS.T_SPOSInvoices.id
left JOIN FoodERP.T_Orders ON FoodERP.T_Orders.id = SweetPOS.TC_SPOSInvoicesReferences.Order
JOIN FoodERP.M_Parties A ON A.id = SweetPOS.T_SPOSInvoices.Party
JOIN FoodERP.M_Parties B ON B.id = SweetPOS.T_SPOSInvoices.Customer
LEFT JOIN FoodERP.M_PriceList ON M_PriceList.id = B.PriceList_id  
JOIN FoodERP.M_PartyType X on A.PartyType_id = X.id
JOIN FoodERP.M_PartyType Y on B.PartyType_id = Y.id
JOIN FoodERP.M_Items ON FoodERP.M_Items.id = SweetPOS.TC_SPOSInvoiceItems.Item
JOIN FoodERP.C_Companies ON FoodERP.C_Companies.id = M_Items.Company_id 
JOIN FoodERP.MC_ItemUnits ON MC_ItemUnits.id = SweetPOS.TC_SPOSInvoiceItems.Unit
JOIN FoodERP.M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
LEFT JOIN FoodERP.M_Drivers ON M_Drivers.id = SweetPOS.T_SPOSInvoices.Driver
LEFT JOIN FoodERP.M_Vehicles ON M_Vehicles.id = SweetPOS.T_SPOSInvoices.Vehicle
left JOIN FoodERP.MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id  and MC_ItemGroupDetails.GroupType_id=5
LEFT JOIN FoodERP.M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id
LEFT JOIN FoodERP.MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
LEFT JOIN FoodERP.M_PartyDetails on  A.id=M_PartyDetails.Party_id AND M_PartyDetails.Group_id is null
LEFT JOIN FoodERP.M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id
LEFT JOIN FoodERP.M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id
WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party in %s'''
               
                Franchises_Data = list(T_SPOSInvoices.objects.raw(query, [FromDate, ToDate,party_tuple_franchise_parties]))  
                Final_Data.extend(Franchises_Data)   
                       
                if Final_Data:
                    GenericSaleData = list()
                    GenericSaleSerializer = GenericSaleReportSerializer(Final_Data, many=True).data

                    GenericSaleData.append({"GenericSaleDetails" : GenericSaleSerializer})
                    log_entry = create_transaction_logNew(request, Genericdata, 0, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 207, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GenericSaleSerializer})
                else:
                    log_entry = create_transaction_logNew(request, Genericdata, 0, 'Report Not available', 207, 0,  FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Genericdata, 0, 'GenericSale:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class RetailerDataView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Retailerdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = Retailerdata['Party']
                if(Party == 0):
                    query = M_Parties.objects.raw('''SELECT M_Parties.id, Supplier.Name SupplierName,M_Parties.Name, M_Parties.isActive, MC_PartySubParty.CreatedOn AS PartyCreation, M_Parties.Email, M_Parties.MobileNo, M_Parties.AlternateContactNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,M_Parties.GSTIN, M_Parties.PAN,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Routes.Name RouteName,C_Companies.Name CompanyName,M_PartyType.Name PartyTypeName, M_PriceList.Name PriceListName, M_Parties.Latitude, M_Parties.Longitude,M_Parties.SAPPartyCode,M_Routes.id Routeid,Supplier.id Supplierid,  M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
FROM MC_PartySubParty
JOIN M_Parties Supplier  ON Supplier.id= MC_PartySubParty.Party_id
JOIN M_Parties  ON M_Parties.id= MC_PartySubParty.SubParty_id
JOIN MC_PartyAddress ON MC_PartyAddress.Party_id =M_Parties.id AND  MC_PartyAddress.IsDefault=1
JOIN M_PartyType ON M_PartyType.id = M_Parties.PartyType_id AND M_PartyType.IsRetailer=1
JOIN M_States ON M_States.id = M_Parties.State_id
JOIN M_Districts ON M_Districts.id = M_Parties.District_id
LEFT JOIN M_Cities ON M_Cities.id=M_Parties.City_id
LEFT JOIN M_PriceList ON M_PriceList.id = M_Parties.PriceList_id
LEFT JOIN C_Companies ON C_Companies.id = M_Parties.Company_id
Left JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN M_PartyDetails on  Supplier.Id=M_PartyDetails.Party_id
JOIN M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id
JOIN M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id
''')
                else:
                    query = M_Parties.objects.raw('''SELECT M_Parties.id, Supplier.Name SupplierName,M_Parties.Name, M_Parties.isActive, MC_PartySubParty.CreatedOn AS PartyCreation, M_Parties.Email, M_Parties.MobileNo, M_Parties.AlternateContactNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,M_Parties.GSTIN, M_Parties.PAN,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Routes.Name RouteName,C_Companies.Name CompanyName,M_PartyType.Name PartyTypeName, M_PriceList.Name PriceListName, M_Parties.Latitude, M_Parties.Longitude,M_Parties.SAPPartyCode,M_Routes.id Routeid,Supplier.id Supplierid,  M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
FROM MC_PartySubParty
JOIN M_Parties Supplier  ON Supplier.id= MC_PartySubParty.Party_id
JOIN M_Parties  ON M_Parties.id= MC_PartySubParty.SubParty_id
JOIN MC_PartyAddress ON MC_PartyAddress.Party_id =M_Parties.id AND  MC_PartyAddress.IsDefault=1
JOIN M_PartyType ON M_PartyType.id = M_Parties.PartyType_id AND M_PartyType.IsRetailer=1
JOIN M_States ON M_States.id = M_Parties.State_id
JOIN M_Districts ON M_Districts.id = M_Parties.District_id
LEFT JOIN M_Cities ON M_Cities.id=M_Parties.City_id
LEFT JOIN M_PriceList ON M_PriceList.id = M_Parties.PriceList_id
LEFT JOIN C_Companies ON C_Companies.id = M_Parties.Company_id
Left JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN M_PartyDetails on  Supplier.Id=M_PartyDetails.Party_id
JOIN M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id
JOIN M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id
WHERE MC_PartySubParty.Party_id=%s''', [Party])

                if query:
                    RetailerExportData = list()
                    RetailerExportSerializer = RetailerDataExportSerializer(
                        query, many=True).data
                    for retailer in RetailerExportSerializer:
                        PartyDateTime =datetime.strptime(retailer['PartyCreation'], "%Y-%m-%d %H:%M:%S")
                        PartyCreation = PartyDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        retailer['PartyCreation'] = PartyCreation
                        
                    RetailerExportData.append(
                        {"ReportExportSerializerDetails": RetailerExportSerializer})
                    log_entry = create_transaction_logNew(
                        request, Retailerdata, Party, '', 208, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': RetailerExportData[0]})
                else:
                    log_entry = create_transaction_logNew(
                        request, Retailerdata, Party, 'Report Not available ', 208, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Retailerdata, 0, 'RetailerData:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

# ================================Stock Processing ================================


class StockProcessingView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                start_date_str = Orderdata['FromDate']
                end_date_str = Orderdata['ToDate']
                Party = Orderdata['Party']

                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

                date_range = []
                current_date = start_date
                while current_date <= end_date:
                    Date = current_date.strftime("%Y-%m-%d")
                    # CustomPrint(Date)
                    # StockDeleteQuery  = O_DateWiseLiveStock.objects.raw('''DELETE FROM O_DateWiseLiveStock WHERE StockDate=%s AND Party_id=%s''',([Date],[Party]))
                    StockDeleteQuery = O_DateWiseLiveStock.objects.filter(
                        Party_id=Party, StockDate=Date)
                    StockDeleteQuery.delete()
                    # CustomPrint(StockDeleteQuery.query)
                    StockProcessQuery = O_DateWiseLiveStock.objects.raw('''select id,ItemID,UnitID,
                    round(OpeningBalance,3) OpeningBalance,
                    round(GRN,3) GRN,
                    round(ProductionQty,3) Production,
                    round(IBPurchaseQuantity,3) IBPurchase,
                    round(IBSaleQuantity,3) IBSale,
                    round(SalesReturn,3) SalesReturn,
                    round(Sale,3) Sale,
                    round(MaterialIssueQuantity,3)MaterialIssue,
                    round(PurchaseReturn,3) PurchaseReturn,
                    round(((OpeningBalance+IBPurchaseQuantity+ProductionQty+GRN+SalesReturn+StockAdjustment)-(Sale+IBSaleQuantity+MaterialIssueQuantity+PurchaseReturn)),3) ClosingBalance,
                    StockAdjustment,ActualStock
 from

(select 1 as id,I.Item_id ItemID,I.UnitID,

(CASE WHEN StockEntry >= 0  THEN IFNULL(StockEntry,0)  ELSE IFNULL(ClosingBalance,0) END )OpeningBalance,
IFNULL(InvoiveQuantity,0)Sale,
IFNULL(GRNQuantity,0)GRN,
IFNULL(SalesReturnQuantity,0)SalesReturn,
IFNULL(PurchesReturnQuantity,0)PurchaseReturn,
IFNULL(StockAdjustmentQTY,0)StockAdjustment,
IFNULL(ActualStock,0)ActualStock,
IFNULL(ProductionQty,0)ProductionQty,
IFNULL(IBSaleQuantity,0)IBSaleQuantity,
IFNULL(IBPurchaseQuantity,0)IBPurchaseQuantity,
IFNULL(MaterialIssueQuantity,0)MaterialIssueQuantity
from

(Select MC_PartyItems.Item_id,MC_ItemUnits.id UnitID
 from MC_PartyItems 
 join M_Items on M_Items.id=MC_PartyItems.Item_id 
 JOIN MC_ItemUnits  ON MC_ItemUnits.UnitID_Id=M_Items.BaseUnitID_id and MC_ItemUnits.Item_id=M_Items.id
 where Party_id=%s AND IsDeleted=0  )I

left join (SELECT IFNULL(Item_id,0) ItemID, sum(ClosingBalance)ClosingBalance FROM O_DateWiseLiveStock WHERE StockDate = DATE_SUB(  %s, INTERVAL 1 
					DAY ) AND Party_id =%s GROUP BY ItemID)CB
                    
on I.Item_id=CB.ItemID

left join (SELECT Item_id,SUM(BaseUnitQuantity) GRNQuantity,SUM(Amount) GRNValue
FROM T_GRNs JOIN TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
WHERE GRNDate = %s AND Customer_id = %s and T_GRNs.IsGRNType=1 GROUP BY Item_id)GRN

on I.Item_id=GRN.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) InvoiveQuantity,SUM(Amount) SaleValue
FROM T_Invoices JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
WHERE InvoiceDate = %s AND Party_id = %s GROUP BY Item_id)Invoice

on I.Item_id=Invoice.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) SalesReturnQuantity,sum(Amount) SalesReturnValue
FROM T_PurchaseReturn join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id      
WHERE ReturnDate = %s AND Party_id = %s and TC_PurchaseReturnItems.ItemReason_id in(SELECT DefaultValue FROM M_Settings where id=14) GROUP BY Item_id)SalesReturn

on I.Item_id=SalesReturn.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) PurchesReturnQuantity,sum(Amount) PurchesReturnValue   
FROM T_PurchaseReturn join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id      
WHERE ReturnDate = %s AND Customer_id = %s and ((TC_PurchaseReturnItems.ItemReason_id IN (SELECT DefaultValue FROM M_Settings WHERE id = 14) and T_PurchaseReturn.Mode =3) OR(T_PurchaseReturn.Mode =2)) GROUP BY Item_id)PurchesReturn
on I.Item_id=PurchesReturn.Item_id

Left join (Select Item_id,SUM(BaseUnitQuantity)StockEntry  from T_Stock where IsDeleted=0 and  IsStockAdjustment=0 and StockDate= DATE_SUB(  %s, INTERVAL 1 DAY ) AND Party_id=%s GROUP BY Item_id)StockEntry 
ON I.Item_id=StockEntry.Item_id

left join (SELECT Item_id,sum(Difference)StockAdjustmentQTY FROM T_Stock where IsDeleted=0 and IsStockAdjustment=1 and StockDate = %s and Party_id= %s group by Item_id)StockAdjustment 
on I.Item_id=StockAdjustment.Item_id

left join (SELECT Item_id,sum(BaseUnitQuantity)ActualStock FROM T_Stock where IsDeleted=0 and IsStockAdjustment=0 and StockDate = %s and Party_id= %s group by Item_id)ActualStock
on I.Item_id=ActualStock.Item_id
                                                                        
left join (select Item_id,sum(ActualQuantity)ProductionQty from T_Production where ProductionDate=%s and Division_id=%s group by Item_id)Production
on I.Item_id=Production.Item_id                                                                        

left join (select Item_id,sum(BaseUnitQuantity)IBSaleQuantity,sum(Amount)IBSalevalue
from T_Challan
join TC_ChallanItems on TC_ChallanItems.Challan_id=T_Challan.id
where ChallanDate = %s and Party_id=%s GROUP BY Item_id)IBSale
on I.Item_id=IBSale.Item_id  

left join (SELECT Item_id,SUM(BaseUnitQuantity) IBPurchaseQuantity,SUM(Amount) IBPurchasevalue
FROM T_GRNs JOIN TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
WHERE GRNDate = %s AND Customer_id = %s and T_GRNs.IsGRNType=0 GROUP BY Item_id)IBPurchase

on I.Item_id=IBPurchase.Item_id 
                                                                        
left join(select MII.Item_id, SUM(IssueQuantity) MaterialIssueQuantity from T_MaterialIssue MI 
join TC_MaterialIssueItems MII on MII.MaterialIssue_id=MI.id
where MI.MaterialIssueDate = %s and Party_id=%s GROUP BY MII.Item_id)MaterialIssue                                                                        
on I.Item_id=MaterialIssue.Item_id)R                                    
where 
OpeningBalance!=0 OR GRN!=0 OR Sale!=0 OR PurchaseReturn != 0 OR SalesReturn !=0 OR StockAdjustment!=0 OR IBPurchaseQuantity !=0 OR IBSaleQuantity != 0 OR ProductionQty != 0 ''',
                                                                        ([Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party]))

                    # print(StockProcessQuery)
                    serializer = StockProcessingReportSerializer(
                        StockProcessQuery, many=True).data
                    # CustomPrint(serializer)
                    for a in serializer: 
                        # print(a)     
                        # print("ItemID:", a["ItemID"], "UnitID:", a["UnitID"])                  
                        stock = O_DateWiseLiveStock(StockDate=Date, OpeningBalance=a["OpeningBalance"], GRN=a["GRN"],Production=a['Production'],MaterialIssue=a["MaterialIssue"],IBSale=a['IBSale'],IBPurchase=a['IBPurchase'], Sale=a["Sale"], PurchaseReturn=a["PurchaseReturn"], SalesReturn=a["SalesReturn"], ClosingBalance=a[
                                                    "ClosingBalance"], ActualStock=a["ActualStock"], StockAdjustment=a["StockAdjustment"], Item_id=a["ItemID"], Unit_id=a["UnitID"], Party_id=Party, CreatedBy=0,  IsAdjusted=0, MRPValue=0)
                        # print("Saving stock:", stock.__dict__)
                        
                        stock.save()
                        
                    current_date += timedelta(days=1)
                log_entry = create_transaction_logNew(request, Orderdata, Party, 'Stock Process Successfully', 209, 0, start_date_str, end_date_str, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Process Successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew( request, Orderdata, 0, 'StockProcessing:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

# ======================================STOCK REPORT=================================


class StockReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Unit = Orderdata['Unit']
                # Party = Orderdata['Party']
                # PartyNameQ = M_Parties.objects.filter(id=Party).values("Name")
                PartyIDs = [int(p) for p in Orderdata['Party'].split(',')]
                
                
                StockData = []
                for Party in PartyIDs:
                    PartyNameQ = M_Parties.objects.filter(id=Party).values("Name")
                    if not PartyNameQ.exists():
                        continue            
                    ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(Party,0).split('!')
                    
                    # UnitName = M_Units.objects.filter(id=Unit).values("Name")
                    # unitname = UnitName[0]['Name']
                    if(Unit!=0):
                        UnitName = M_Units.objects.filter(id=Unit).values("Name")
                        unitname = UnitName[0]['Name']                    
                    else:
                        unitname =''
                        
                    # print('aaaaa')
                    if(Unit==0):
                        unitcondi='A.Unit_id'
                        unitcondiPOS='A.Unit'
                    else:
                        unitcondi=Unit  
                        unitcondiPOS=Unit
                    StockreportQuery = O_DateWiseLiveStock.objects.raw(f'''SELECT  1 as id,A.Item_id,A.Unit_id,
                    UnitwiseQuantityConversion(A.Item_id,ifnull(OpeningBalance,0),0,A.Unit_id,0,{unitcondi},0)OpeningBalance, 
                    UnitwiseQuantityConversion(A.Item_id,GRNInward,0,A.Unit_id,0,{unitcondi},0)GRNInward, 
                    UnitwiseQuantityConversion(A.Item_id,Production,0,A.Unit_id,0,{unitcondi},0)Production,
                    UnitwiseQuantityConversion(A.Item_id,IBSale,0,A.Unit_id,0,{unitcondi},0)IBSale,
                    UnitwiseQuantityConversion(A.Item_id,MaterialIssue,0,A.Unit_id,0,{unitcondi},0)MaterialIssue,
                    UnitwiseQuantityConversion(A.Item_id,IBPurchase,0,A.Unit_id,0,{unitcondi},0)IBPurchase,
                    UnitwiseQuantityConversion(A.Item_id,Sale,0,A.Unit_id,0,{unitcondi},0)Sale, 
                    UnitwiseQuantityConversion(A.Item_id,ifnull(ClosingBalance,0),0,A.Unit_id,0,{unitcondi},0)ClosingBalance, 
                    UnitwiseQuantityConversion(A.Item_id,ifnull(ActualStock,0),0,A.Unit_id,0,{unitcondi},0)ActualStock,
                    A.ItemName,
                    D.QuantityInBaseUnit,
                    UnitwiseQuantityConversion(A.Item_id,PurchaseReturn,0,A.Unit_id,0,{unitcondi},0)PurchaseReturn,
                    UnitwiseQuantityConversion(A.Item_id,SalesReturn,0,A.Unit_id,0,{unitcondi},0)SalesReturn,
                    UnitwiseQuantityConversion(A.Item_id,StockAdjustment,0,A.Unit_id,0,{unitcondi},0)StockAdjustment
                    ,GroupTypeName,GroupName,SubGroupName,CASE WHEN {Unit} = 0 THEN UnitName else '{unitname}' END UnitName
                    ,(FoodERP.RateCalculationFunction1(0, A.Item_id, {Party}, A.Unit_id, 0, 0, 0, 1) * FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(ClosingBalance,0),0,A.Unit_id,0,{unitcondi},0))ClosingAmount
                    FROM 
        
        ( SELECT M_Items.id Item_id, M_Items.Name ItemName ,M_Units.id Unit_id,M_Units.Name UnitName,sum(MaterialIssue)MaterialIssue, SUM(Production)Production,SUM(GRN) GRNInward, SUM(Sale) Sale,SUM(IBSale) IBSale,SUM(IBPurchase) IBPurchase, SUM(PurchaseReturn)PurchaseReturn,SUM(SalesReturn)SalesReturn,SUM(StockAdjustment)StockAdjustment,
        {ItemsGroupJoinsandOrderby[0]}
        FROM O_DateWiseLiveStock
        
            JOIN M_Items ON M_Items.id=O_DateWiseLiveStock.Item_id 
            join MC_ItemUnits on MC_ItemUnits.id=O_DateWiseLiveStock.Unit_id
            JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
            {ItemsGroupJoinsandOrderby[1]} 
            
            WHERE StockDate BETWEEN %s AND %s AND Party_id=%s GROUP BY Item_id,Unit_id,GroupType.id,Groupss.id,subgroup.id
            {ItemsGroupJoinsandOrderby[2]}) A 
            
            left JOIN (SELECT O_DateWiseLiveStock.Item_id, OpeningBalance FROM O_DateWiseLiveStock WHERE O_DateWiseLiveStock.StockDate = %s AND O_DateWiseLiveStock.Party_id=%s) B
            
            ON A.Item_id = B.Item_id 
            
            left JOIN (SELECT Item_id, ClosingBalance, ActualStock FROM O_DateWiseLiveStock WHERE StockDate = %s AND Party_id=%s) C
            
            ON A.Item_id = C.Item_id  
            
            LEFT JOIN (SELECT Item_id, SUM(BaseunitQuantity) QuantityInBaseUnit 
            FROM T_Stock 
            WHERE Party_id =%s AND StockDate BETWEEN %s AND %s 
            GROUP BY Item_id) D 		
            ON A.Item_id = D.Item_id
             
            UNION
               
                  SELECT 1 as id,A.Item_id,A.Unit,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(OpeningBalance,0),0,A.Unit,0,{unitcondiPOS},0)OpeningBalance,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(GRNInward,0),0,A.Unit,0,{unitcondiPOS},0)GRNInward,
                    0 Production,
                    0 IBSale,
                    0 MaterialIssue,
                    0 IBPurchase,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(Sale,0),0,A.Unit,0,{unitcondiPOS},0)Sale,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(ClosingBalance,0),0,A.Unit,0,{unitcondiPOS},0)ClosingBalance,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(ActualStock,0),0,A.Unit,0,{unitcondiPOS},0)ActualStock,
                    
                    A.ItemName,
                    D.QuantityInBaseUnit,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(PurchaseReturn,0),0,A.Unit,0,{unitcondiPOS},0)PurchaseReturn,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(SalesReturn,0),0,A.Unit,0,{unitcondiPOS},0)SalesReturn,
                    FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(StockAdjustment,0),0,A.Unit,0,{unitcondiPOS},0)StockAdjustment
                    ,GroupTypeName,GroupName,SubGroupName,
                    CASE WHEN {Unit} = 0 THEN UnitName else '{unitname}' END UnitName,               
                    (FoodERP.RateCalculationFunction1(0, A.Item_id, {Party}, A.Unit, 0, 0, 0, 1) * FoodERP.UnitwiseQuantityConversion(A.Item_id,ifnull(ClosingBalance,0),0,A.Unit,0,{unitcondiPOS},0))ClosingAmount
                    FROM                                                                           
                    ( SELECT M_Items.id Item_id, M_Items.Name ItemName ,M_Units.id Unit,M_Units.Name UnitName,SUM(GRN) GRNInward, SUM(Sale) Sale, SUM(PurchaseReturn)PurchaseReturn,SUM(SalesReturn)SalesReturn,SUM(StockAdjustment)StockAdjustment,
                        {ItemsGroupJoinsandOrderby[0]}
                        FROM SweetPOS.O_SPOSDateWiseLiveStock SPOSDatewise

                    JOIN FoodERP.M_Items ON M_Items.id=SPOSDatewise.Item
                    join FoodERP.MC_ItemUnits on MC_ItemUnits.id= SPOSDatewise.Unit
                    JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
                    {ItemsGroupJoinsandOrderby[1]}
                    WHERE StockDate BETWEEN %s AND %s AND Party=%s    GROUP BY Item,Unit,GroupType.id,Groupss.id,subgroup.id
                    {ItemsGroupJoinsandOrderby[2]}) A

                    left JOIN (SELECT Item, OpeningBalance FROM SweetPOS.O_SPOSDateWiseLiveStock WHERE StockDate = %s AND Party=%s) B
                    ON A.Item_id = B.Item

                    left JOIN (SELECT Item, ClosingBalance, ActualStock FROM SweetPOS.O_SPOSDateWiseLiveStock WHERE StockDate = %s AND Party=%s) C 
                    ON A.Item_id = C.Item

                    LEFT JOIN (SELECT Item, SUM(BaseunitQuantity) QuantityInBaseUnit
                    FROM SweetPOS.T_SPOSStock
                    WHERE Party =%s AND StockDate BETWEEN %s AND %s
                    GROUP BY Item) D
                    ON A.Item_id = D.Item    ''', ([FromDate], [ToDate], [Party], [FromDate], [Party], [ToDate], [Party], [Party], [FromDate], [ToDate],[FromDate], [ToDate], [Party], [FromDate], [Party], [ToDate], [Party], [Party], [FromDate], [ToDate]))
                    # print(StockreportQuery)
                    # serializer = StockReportSerializer(StockreportQuery, many=True).data
                    # print(serializer )
                    # StockData = list()
                    
                    StockDetails =list()
                    if StockreportQuery:
                    
                        for a in StockreportQuery:
                            # print(a.Sale)
                            StockDetails.append({
                                "Item_id": a.Item_id,
                                "Unit_id": a.Unit_id,
                                "UnitName":  a.UnitName,
                                "OpeningBalance":  round(a.OpeningBalance,3),
                                "GRNInward":  round(a.GRNInward,3),
                                "SalesReturn" : round(a.SalesReturn,3),
                                "Sale" :  round(a.Sale,3),
                                "PurchaseReturn" : round(a.PurchaseReturn,3),  
                                "ClosingBalance":  round(a.ClosingBalance,3),
                                "ClosingAmount" : round(a.ClosingAmount,3),
                                "ActualStock":  round(a.ActualStock,3),
                                "ItemName" : a.ItemName,
                                "GroupTypeName" : a.GroupTypeName,
                                "GroupName" : a.GroupName,
                                "SubGroupName" : a.SubGroupName,
                                "StockAdjustment":  round(a.StockAdjustment,3),
                                "Production" :  round(a.Production,3),
                                "IBPurchase" :  round(a.IBPurchase,3),
                                "IBSale"  :  round(a.IBSale,3),
                                "MaterialIssue" :  round(a.MaterialIssue,3)

                             })
                        StockData.append({
                        "FromDate": FromDate,
                        "ToDate": ToDate,
                        "PartyName": PartyNameQ[0]["Name"],
                        "StockDetails": StockDetails
                        })

                if StockData:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 210, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': StockData})
                else:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'Recort Not Found', 210, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Orderdata, 0, 'StockReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


# select I.Item_id,I.ItemName,InvoiveQuantity,InvoiceMRP,GRNQuantity,GRNMRP,StockQuantity,StockMRP,SalesReturnQuantity,SalesReturnMRP,PurchesReturnQuantity,PurchesReturnMRP from

# (Select Item_id ,M_Items.Name ItemName from MC_PartyItems join M_Items on M_Items.id=MC_PartyItems.Item_id where Party_id=14)I

# left join
# (SELECT
#     Item_id,
#     MRPValue GRNMRP,
#     SUM(BaseUnitQuantity) GRNQuantity,
#     SUM(Amount) GRNValue
# FROM
#     T_GRNs
#         JOIN
#     TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
# WHERE
#     GRNDate = '2023-07-21' AND Customer_id = 14
# GROUP BY Item_id,MRPValue)b


# on I.Item_id=b.Item_id

# left join
# (SELECT
#     Item_id,
#     MRPValue InvoiceMRP,
#     SUM(BaseUnitQuantity) InvoiveQuantity,
#     SUM(Amount) SaleValue
# FROM
#     T_Invoices
#         JOIN
#     TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
# WHERE
#     InvoiceDate = '2023-07-21'AND Party_id = 14
# GROUP BY Item_id,MRPValue)a
# on I.Item_id=a.Item_id  and b.GRNMRP=a.InvoiceMRP
# left join


# (SELECT
#     Item_id,
#     MRPValue StockMRP,
#     SUM(BaseUnitQuantity) StockQuantity
# FROM
#     T_Stock
# WHERE
#     StockDate = '2023-07-21' AND Party_id = 14
# GROUP BY Item_id,MRPValue)c

# on I.Item_id=c.Item_id and b.GRNMRP=c.StockMRP
# left join

# (SELECT
#     Item_id,
#     MRPValue SalesReturnMRP,
#     SUM(BaseUnitQuantity) SalesReturnQuantity,
#     sum(Amount) SalesReturnValue
# FROM
#     T_PurchaseReturn
#     join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
# WHERE
#     ReturnDate = '2023-07-21' AND Party_id = 14
# GROUP BY Item_id,MRPValue)d

# on I.Item_id=d.Item_id and b.GRNMRP=d.SalesReturnMRP
# left join
# (SELECT
#     Item_id,
#     MRPValue PurchesReturnMRP,
#     SUM(BaseUnitQuantity) PurchesReturnQuantity,
#     sum(Amount) PurchesReturnValue
# FROM
#     T_PurchaseReturn
#     join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
# WHERE
#     ReturnDate = '2023-07-21' AND Customer_id = 14
# GROUP BY Item_id,MRPValue)e
# on I.Item_id=e.Item_id and b.GRNMRP=e.PurchesReturnMRP

class PurchaseGSTReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Customer = Reportdata['Party']
                GSTRatewise = Reportdata['GSTRatewise']

                if GSTRatewise == 1:

                    query = TC_GRNReferences.objects.raw(
                        '''SELECT 1 As id, GSTPercentage,  SUM(BasicAmount) TaxableValue, SUM(CGST) CGST, SUM( SGST) SGST, SUM( IGST) IGST, SUM(GSTAmount) GSTAmount, SUM(Amount) TotalValue   FROM TC_GRNReferences JOIN T_Invoices ON T_Invoices.id =TC_GRNReferences.Invoice_id JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Customer_id= %s and DeletedFromSAP=0 GROUP BY TC_InvoiceItems.GSTPercentage''', ([FromDate], [ToDate], [Customer]))
                    if query:
                        PurchaseGSTRateWiseData = list()
                        PurchaseGSTRateWiseSerializer = PurchaseGSTRateWiseReportSerializer(
                            query, many=True).data
                        PurchaseGSTRateWiseData.append(
                            {"PurchaseGSTRateWiseDetails": PurchaseGSTRateWiseSerializer})
                        log_entry = create_transaction_logNew(request, Reportdata, Customer, 'From:'+str(
                            FromDate)+'To:'+str(ToDate), 211, 0, FromDate, ToDate, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PurchaseGSTRateWiseData[0]})
                    else:
                        log_entry = create_transaction_logNew(
                            request, Reportdata, Customer, 'Report Not available', 211, 0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
                else:
                    query = TC_GRNReferences.objects.raw(
                        '''SELECT 1 AS id,M_Parties.Name,InvoiceNumber,FullInvoiceNumber,InvoiceDate,SUM(CGSTPercentage + SGSTPercentage + IGSTPercentage) GSTRate,GSTPercentage,SUM(BasicAmount) TaxableValue,SUM(CGST) CGST,SUM(SGST) SGST,SUM(IGST) IGST,SUM(GSTAmount) GSTAmount,SUM(TC_InvoiceItems.DiscountAmount) DiscountAmount,SUM(Amount) TotalValue FROM TC_GRNReferences JOIN T_Invoices ON T_Invoices.id = TC_GRNReferences.Invoice_id JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id JOIN M_Parties ON T_Invoices.Party_id = M_Parties.id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Customer_id =%s and DeletedFromSAP=0 GROUP BY M_Parties.id, T_Invoices.InvoiceNumber, T_Invoices.FullInvoiceNumber, T_Invoices.InvoiceDate, TC_InvoiceItems.GSTPercentage''', ([FromDate], [ToDate], [Customer]))
                    if query:
                        PurchaseGSTSerializer = PurchaseGSTReportSerializer(
                            query, many=True).data
                        # CustomPrint(PurchaseGSTSerializer)
                        PurchaseGSTData = list()
                        PurchaseGSTData.append(
                            {"PurchaseGSTDetails": PurchaseGSTSerializer})
                        log_entry = create_transaction_logNew(request, Reportdata, Customer, 'From:'+str(
                            FromDate)+'To:'+str(ToDate), 211, 0, FromDate, ToDate, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PurchaseGSTData[0]})
                    else:
                        log_entry = create_transaction_logNew(request, Reportdata, Customer, '', 211, 0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'PurchaseGSTReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class InvoiceDateExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Customer = Reportdata['Customer']
                Employee = Reportdata['Employee']
                Mode = Reportdata['Mode']
                if Employee > 0:
                    EmpPartys = MC_EmployeeParties.objects.raw(
                        '''select EmployeeParties(%s) id''', [Employee])
                    for row in EmpPartys:
                        p = row.id
                    PartyIDs = p.split(",")

                if (Mode == 1):

                    Invoicequery ='''SELECT TC_InvoiceItems.id,T_Invoices.Party_id AS SupplierID,A.Name SupplierName,T_Invoices.FullInvoiceNumber As InvoiceNumber,T_Invoices.InvoiceDate,T_Invoices.Customer_id As CustomerID,B.Name CustomerName,TC_InvoiceItems.Item_id AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_InvoiceItems.MRPValue AS MRP,TC_InvoiceItems.QtyInNo,TC_InvoiceItems.QtyInKg,TC_InvoiceItems.QtyInBox,TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate +((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType, TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,TC_InvoiceItems.BasicAmount As TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,TC_InvoiceItems.GSTPercentage,TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Invoices.TCSAmount,T_Invoices.RoundOffAmount,T_Invoices.GrandTotal,'' AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_InvoiceUploads.Irn, TC_InvoiceUploads.AckNo,TC_InvoiceUploads.EwayBillNo, M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName
                                            FROM TC_InvoiceItems
                                            JOIN T_Invoices ON T_Invoices.id =TC_InvoiceItems.Invoice_id
                                            LEFT JOIN TC_InvoicesReferences ON TC_InvoicesReferences.Invoice_id=T_Invoices.id
                                            LEFT JOIN T_Orders ON T_Orders.id = TC_InvoicesReferences.Order_id
                                            
                                            JOIN M_Parties A ON A.id= T_Invoices.Party_id
                                            JOIN M_Parties B ON B.id = T_Invoices.Customer_id
                                            JOIN M_States ON M_States.id = B.State_id
                                            JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id
                                            JOIN C_Companies ON C_Companies.id = M_Items.Company_id
                                            JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                                            JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
                                            JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
                                            JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_Invoices.Customer_id 
                                            LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
                                            LEFT JOIN TC_InvoiceUploads on TC_InvoiceUploads.Invoice_id = T_Invoices.id
                                            left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
                                            LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                                            LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
                                            WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s '''

                    if Party == 0:
                        if Employee == 0:
                            Invoicequery += " "
                        else:
                            Invoicequery += "and MC_PartySubParty.Party_id in %s"
                    else:
                        Invoicequery += " and MC_PartySubParty.Party_id=%s"

                    if Party == 0:
                        if Employee == 0:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate])
                        else:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate, PartyIDs])
                    else:

                        InvoiceQueryresults = T_Invoices.objects.raw(Invoicequery,[FromDate,ToDate,Party])      
                else: 
                    Invoicequery= f'''SELECT TC_InvoiceItems.id,T_Invoices.Party_id AS SupplierID,A.Name SupplierName,T_Invoices.FullInvoiceNumber As InvoiceNumber,T_Invoices.InvoiceDate,T_Invoices.Customer_id As CustomerID,B.Name CustomerName,TC_InvoiceItems.Item_id AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,GSTHsnCodeMaster(TC_InvoiceItems.Item_id,T_Invoices.InvoiceDate ,3,{Customer},0)HSNCode,TC_InvoiceItems.MRPValue AS MRP,TC_InvoiceItems.QtyInNo,TC_InvoiceItems.QtyInKg,TC_InvoiceItems.QtyInBox,TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate +((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType, TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,TC_InvoiceItems.BasicAmount As TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,GSTHsnCodeMaster(TC_InvoiceItems.Item_id,T_Invoices.InvoiceDate ,2,{Customer},0)GSTPercentage,TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Invoices.TCSAmount,T_Invoices.RoundOffAmount,T_Invoices.GrandTotal,'' AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_InvoiceUploads.Irn, TC_InvoiceUploads.AckNo,TC_InvoiceUploads.EwayBillNo, M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName
    FROM TC_InvoiceItems
    JOIN T_Invoices ON T_Invoices.id =TC_InvoiceItems.Invoice_id
    join TC_GRNReferences on TC_GRNReferences.Invoice_id = T_Invoices.id
    JOIN M_Parties A ON A.id= T_Invoices.Party_id
    JOIN M_Parties B ON B.id = T_Invoices.Customer_id
    JOIN M_States ON M_States.id = B.State_id
    JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id
    JOIN C_Companies ON C_Companies.id = M_Items.Company_id
    JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
    JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id    
    LEFT JOIN TC_InvoiceUploads on TC_InvoiceUploads.Invoice_id = T_Invoices.id
    left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
    LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
    LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
    WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s'''
                    
                    if Customer == 0:
                        if Employee == 0:
                            Invoicequery += " "
                        else:
                            Invoicequery += "AND  T_Invoices.Customer_id in %s"
                    else:
                        Invoicequery += " AND  T_Invoices.Customer_id=%s"

                    if Customer == 0:
                        if Employee == 0:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate])
                        else:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate, PartyIDs])
                            
                    else:

                        InvoiceQueryresults = T_Invoices.objects.raw(Invoicequery,[FromDate,ToDate,Customer])
                        
                       
                if InvoiceQueryresults:

                    InvoiceExportData = list()
                    InvoiceExportSerializer = InvoiceDataExportSerializer(
                        InvoiceQueryresults, many=True).data
                    for b in InvoiceExportSerializer:

                        qur2 = M_Parties.objects.filter(id=b['CustomerID']).values('PriceList').distinct()
                        
                        query = M_PriceList.objects.values('id').filter(id__in=qur2)

                        Rate = RateCalculationFunction(0, b['FE2MaterialID'], 0, 0, 1, 0, query[0]['id']).RateWithGST()
                        
                        NoRate = float(Rate[0]['NoRatewithOutGST'])
                        InvoiceExportData.append({

                            
                            "SupplierID":b['SupplierID'],
                            "SupplierName":b['SupplierName'],
                            "InvoiceNumber":b['InvoiceNumber'],
                            "InvoiceDate":b['InvoiceDate'],
                            "CustomerID":b['CustomerID'],
                            "CustomerName":b['CustomerName'],
                            "FE2MaterialID":b['FE2MaterialID'],
                            "MaterialName":b['MaterialName'],
                            "CompanyName":b['CompanyName'],
                            "HSNCode":b['HSNCode'],
                            "MRP":b['MRP'],
                            "QtyInNo":b['QtyInNo'],
                            "QtyInKg":b['QtyInKg'],
                            "QtyInBox":b['QtyInBox'],
                            "BasicRate":b['BasicRate'],
                            "WithGSTRate":b['WithGSTRate'],
                            "NoRate":NoRate,
                            "UnitName":b['UnitName'],
                            "DiscountType":b['DiscountType'],
                            "Discount":b['Discount'],
                            "DiscountAmount":b['DiscountAmount'],
                            "TaxableValue":b['TaxableValue'],
                            "CGST":b['CGST'],
                            "CGSTPercentage":b['CGSTPercentage'],
                            "SGST":b['SGST'],
                            "SGSTPercentage":b['SGSTPercentage'],
                            "IGST":b['IGST'],
                            "IGSTPercentage":b['IGSTPercentage'],
                            "GSTPercentage":b['GSTPercentage'],
                            "GSTAmount":b['GSTAmount'],
                            "TotalValue":b['TotalValue'],
                            "TCSAmount":b['TCSAmount'],
                            "RoundOffAmount":b['RoundOffAmount'],
                            "GrandTotal":b['GrandTotal'],
                            "RouteName":b['RouteName'],
                            "StateName":b['StateName'],
                            "GSTIN":b['GSTIN'],
                            "Irn":b['Irn'],
                            "AckNo":b['AckNo'],
                            "EwayBillNo":b['EwayBillNo'],
                            "GroupName": b['GroupName'],
                            "SubGroupName" :b['SubGroupName'],

                        })
                    # InvoiceExportData.append({"InvoiceExportSerializerDetails" : InvoiceExportSerializer})
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 212, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceExportData})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'Report Not available', 212, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'InvoiceDateExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class DeletedInvoiceDateExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                query = T_DeletedInvoices.objects.raw('''SELECT TC_DeletedInvoiceItems.id,T_DeletedInvoices.Party AS SupplierID,A.Name SupplierName,T_DeletedInvoices.FullInvoiceNumber As InvoiceNumber,T_DeletedInvoices.InvoiceDate,T_DeletedInvoices.Customer As CustomerID,B.Name CustomerName,TC_DeletedInvoiceItems.Item AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_DeletedInvoiceItems.MRPValue AS MRP,TC_DeletedInvoiceItems.QtyInNo,TC_DeletedInvoiceItems.QtyInKg,TC_DeletedInvoiceItems.QtyInBox,TC_DeletedInvoiceItems.Rate AS BasicRate,(TC_DeletedInvoiceItems.Rate +((TC_DeletedInvoiceItems.Rate * TC_DeletedInvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_DeletedInvoiceItems.DiscountType, TC_DeletedInvoiceItems.Discount,TC_DeletedInvoiceItems.DiscountAmount,TC_DeletedInvoiceItems.BasicAmount As TaxableValue,TC_DeletedInvoiceItems.CGST,TC_DeletedInvoiceItems.CGSTPercentage,TC_DeletedInvoiceItems.SGST,TC_DeletedInvoiceItems.SGSTPercentage,TC_DeletedInvoiceItems.IGST,TC_DeletedInvoiceItems.IGSTPercentage,TC_DeletedInvoiceItems.GSTPercentage,TC_DeletedInvoiceItems.GSTAmount,TC_DeletedInvoiceItems.Amount AS TotalValue,T_DeletedInvoices.TCSAmount,T_DeletedInvoices.RoundOffAmount,T_DeletedInvoices.GrandTotal,M_Routes.Name AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_DeletedInvoiceUploads.Irn, TC_DeletedInvoiceUploads.AckNo,TC_DeletedInvoiceUploads.EwayBillNo,
 M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName
FROM TC_DeletedInvoiceItems
JOIN T_DeletedInvoices ON T_DeletedInvoices.Invoice =TC_DeletedInvoiceItems.Invoice
JOIN M_Parties A ON A.id= T_DeletedInvoices.Party
JOIN M_Parties B ON B.id = T_DeletedInvoices.Customer
JOIN M_States ON M_States.id = B.State_id
JOIN M_Items ON M_Items.id = TC_DeletedInvoiceItems.Item
JOIN C_Companies ON C_Companies.id = M_Items.Company_id
JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_DeletedInvoiceItems.GST
JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_DeletedInvoiceItems.Unit
JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_DeletedInvoices.Customer AND MC_PartySubParty.Party_id=%s
LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN TC_DeletedInvoiceUploads on TC_DeletedInvoiceUploads.Invoice= T_DeletedInvoices.id
left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id

WHERE T_DeletedInvoices.InvoiceDate BETWEEN %s AND %s AND  T_DeletedInvoices.Party=%s ''', ([Party], [FromDate], [ToDate], [Party]))

                if query:
                    DeletedInvoiceExportData = list()
                    DeletedInvoiceExportSerializer = InvoiceDataExportSerializer(query, many=True).data
                    DeletedInvoiceExportData.append(
                        {"DeletedInvoiceExportSerializerDetails": DeletedInvoiceExportSerializer})
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'From:'+str(FromDate)+'To:'+str(ToDate), 213, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DeletedInvoiceExportData[0]})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'Report Not available', 213, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'DeletedInvoiceDateExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class StockDamageReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Damagedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Damagedata['FromDate']
                ToDate = Damagedata['ToDate']
                PartyID = Damagedata['PartyID']
                ConversionUnit = Damagedata['Unit']

                query1 = M_Units.objects.filter(
                    id=ConversionUnit).values('Name')
                query = O_BatchWiseLiveStock.objects.raw(
                    '''SELECT M_Items.id, M_Items.Name ItemName, SUM(BaseUnitQuantity) Qty,M_Units.id UnitID,O_LiveBatches.MRPValue FROM O_BatchWiseLiveStock JOIN M_Items ON M_Items.id=O_BatchWiseLiveStock.Item_id JOIN M_Units ON M_Units.id=M_Items.BaseUnitID_id JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id WHERE O_BatchWiseLiveStock.Party_id=%s AND O_BatchWiseLiveStock.IsDamagePieces=1 AND O_BatchWiseLiveStock.BaseUnitQuantity>0  GROUP BY O_BatchWiseLiveStock.Item_id,O_LiveBatches.MRPValue''', ([PartyID]))
                if query:
                    DamageStockData = list()
                    DamageItemStocktSerializer = DamageStocktSerializer(
                        query, many=True).data
                    for a in DamageItemStocktSerializer:
                        ConversionUnitQty = UnitwiseQuantityConversion(
                            a['id'], a['Qty'], 0, a['UnitID'], 0, ConversionUnit, 0).ConvertintoSelectedUnit()
                        DamageStockData.append({
                            "Item": a['id'],
                            "ItemName": a['ItemName'],
                            "ActualQty": ConversionUnitQty,
                            "Unit": query1[0]['Name'],
                            "MRP": a['MRPValue']
                        })
                    log_entry = create_transaction_logNew(request, Damagedata, 0, '', 415, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DamageStockData})
                else:
                    log_entry = create_transaction_logNew(request, Damagedata, 0, 'Records Not available', 415, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Damagedata, 0, 'DamageStock:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ReturnReportDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Party_list = Party.split(",")
                query = T_PurchaseReturn.objects.raw('''select *,M_Routes.Name RouteName from (SELECT T_PurchaseReturn.id, T_PurchaseReturn.ReturnDate,B.Name CustomerName,D.Name CustomerType,C_Companies.Name CompanyName,
                                                      M_Group.Name Product,MC_SubGroup.Name SubProduct, M_Items.id AS ERPItemCode, M_Items.SAPItemCode, M_Items.Name MaterialName,TC_PurchaseReturnItems.Quantity ReturnQtyNos,
                                                     TC_PurchaseReturnItems.MRPValue,TC_PurchaseReturnItems.Rate, TC_PurchaseReturnItems.BasicAmount,
                                                     TC_PurchaseReturnItems.GSTPercentage, TC_PurchaseReturnItems.GSTAmount, TC_PurchaseReturnItems.Amount,
                                                     TC_PurchaseReturnItems.Discount,TC_PurchaseReturnItems.DiscountAmount,TC_PurchaseReturnItems.DiscountType,
                                                     TC_PurchaseReturnItems.BatchDate, TC_PurchaseReturnItems.BatchCode,M_GeneralMaster.Name ReasonForReturn,
                                                     TC_PurchaseReturnItems.ApprovedQuantity ApprovedQuantityInNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,
                                                     A.Name SupplierName,C.Name SupplierType,T_PurchaseReturn.FullReturnNumber,
                                                     ApprovedByCompany,FinalApprovalDate,ApprovedRate,ApprovedBasicAmount,ApprovedGSTPercentage,ApprovedCGST,
                                                     ApprovedIGST,ApprovedSGST,ApprovedCGSTPercentage,ApprovedSGSTPercentage,ApprovedIGSTPercentage,
                                                     ApprovedGSTAmount,ApprovedAmount,ApprovedDiscountAmount ,A.id PartyID,B.id CustomerID
                                                     FROM TC_PurchaseReturnItems 
                                                     JOIN T_PurchaseReturn ON T_PurchaseReturn.id =TC_PurchaseReturnItems.PurchaseReturn_id 
                                                     JOIN M_Parties A ON A.id= T_PurchaseReturn.Party_id 
                                                     JOIN M_Parties B ON B.id = T_PurchaseReturn.Customer_id 
                                                     JOIN M_PartyType C  ON C.id= A.PartyType_id 
                                                     JOIN M_PartyType D ON D.id= B.PartyType_id 
                                                     Left JOIN MC_PartyAddress ON MC_PartyAddress.Party_id=B.id AND MC_PartyAddress.IsDefault=1 
                                                     
                                                     JOIN M_Items ON M_Items.id = TC_PurchaseReturnItems.Item_id 
                                                     LEFT JOIN MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1 
                                                     LEFT JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
                                                     LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                                                     LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
                                                     JOIN M_GeneralMaster ON M_GeneralMaster.id = TC_PurchaseReturnItems.ItemReason_id 
                                                     JOIN C_Companies ON C_Companies.id = M_Items.Company_id 
                                                     WHERE T_PurchaseReturn.ReturnDate BETWEEN %s AND %s AND  (T_PurchaseReturn.Party_id IN %s OR T_PurchaseReturn.Customer_id IN %s)  
                                                     Order by T_PurchaseReturn.ReturnDate,T_PurchaseReturn.Customer_id)PP
                                                     JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = PP.CustomerID and MC_PartySubParty.Party_id=PP.PartyID
                                                     LEFT JOIN M_Routes ON M_Routes.id = MC_PartySubParty.Route_id
                                                       ''', ([
                                                      FromDate, ToDate, Party_list,Party_list]))
                # print(query.query)
                if query:
                    ReturnSerializer = ReturnReportSerializer(
                        query, many=True).data
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'From:'+str( FromDate)+','+'To:'+str(ToDate), 214, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReturnSerializer})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'Report Not available', 214, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'ReturnReportDownload:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class MaterialRegisterDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Item = Reportdata['Item']
                Unit = Reportdata['Unit']               
                    
                q1 = M_Items.objects.filter(id=Item).values('BaseUnitID_id')
                BaseUnitID = q1[0]['BaseUnitID_id']                
                if Unit==0:
                    Unit=BaseUnitID                    
                q3 =  M_Units.objects.filter(id=Unit).values('Name')
                UnitName=q3[0]['Name']                
                q2 = M_Settings.objects.filter(id=14).values('DefaultValue')
                DefaultValues = q2[0]['DefaultValue']

                query = T_PurchaseReturn.objects.raw(f'''SELECT 1 as id,a.* from (SELECT 1 Sequence, T_GRNs.GRNDate TransactionDate,T_GRNs.CreatedOn,T_GRNs.FullGRNNumber TransactionNumber,M_Parties.Name,
                UnitwiseQuantityConversion({Item},Quantity,TC_GRNItems.Unit_id,0,0,{Unit},0)Quantity,TC_GRNItems.Unit_id  FROM T_GRNs 
JOIN TC_GRNItems ON TC_GRNItems.GRN_id=T_GRNs.id
JOIN M_Parties ON M_Parties.id = T_GRNs.Party_id
WHERE GRNDate Between %s AND %s AND Customer_id=%s and TC_GRNItems.Item_id=%s and T_GRNs.IsGRNType=1

UNION ALL

SELECT 2 Sequence, T_PurchaseReturn.ReturnDate TransactionDate,T_PurchaseReturn.CreatedOn ,
T_PurchaseReturn.FullReturnNumber TransactionNumber,M_Parties.Name,
UnitwiseQuantityConversion({Item},Quantity,TC_PurchaseReturnItems.Unit_id,0,0,{Unit},0)Quantity,TC_PurchaseReturnItems.Unit_id  FROM T_PurchaseReturn 
JOIN TC_PurchaseReturnItems ON TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
JOIN M_Parties ON M_Parties.id = T_PurchaseReturn.Customer_id
WHERE ReturnDate Between %s AND  %s AND Party_id=%s AND TC_PurchaseReturnItems.Item_id=%s AND TC_PurchaseReturnItems.ItemReason_id IN (%s)

UNION ALL

SELECT 3 Sequence, StockDate TransactionDate,CreatedOn, FullReturnNumber TransactionNumber, Name, 
UnitwiseQuantityConversion({Item},QStock,Unit_id,0,0,{Unit},0)Quantity,Unit_id
FROM (SELECT 3 Sequence,T_Stock.StockDate,T_Stock.CreatedOn ,'STOCK' FullReturnNumber,M_Parties.Name, ''Quantity, SUM(T_Stock.BaseUnitQuantity) QStock,Unit_id 
From T_Stock
 JOIN M_Parties ON M_Parties.id=T_Stock.Party_id  
 WHERE StockDate Between %s AND %s AND Party_id=%s  AND  T_Stock.Item_id=%s and IsStockAdjustment=0 GROUP BY 3 ,T_Stock.StockDate, FullReturnNumber,M_Parties.Name,Quantity)AA

UNION ALL

SELECT 6 Sequence, StockDate TransactionDate,CreatedOn, FullReturnNumber TransactionNumber, Name, UnitwiseQuantityConversion({Item},QStock,Unit_id,0,0,{Unit},0)Quantity,Unit_id
FROM (SELECT 3 Sequence,T_Stock.StockDate,T_Stock.CreatedOn ,'Stock Adjustment' FullReturnNumber,M_Parties.Name, '' Quantity, SUM(T_Stock.Difference) QStock,Unit_id 
From T_Stock
 JOIN M_Parties ON M_Parties.id=T_Stock.Party_id  
 WHERE StockDate Between %s AND %s AND Party_id=%s  AND  T_Stock.Item_id=%s and IsStockAdjustment =1 GROUP BY 3 ,T_Stock.StockDate, FullReturnNumber,M_Parties.Name,Quantity)AA

UNION ALL

SELECT 4 Sequence, T_Invoices.InvoiceDate TransactionDate,T_Invoices.CreatedOn,
T_Invoices.FullInvoiceNumber TransactionNumber,M_Parties.Name,
UnitwiseQuantityConversion({Item},Quantity,TC_InvoiceItems.Unit_id,0,0,{Unit},0)Quantity,TC_InvoiceItems.Unit_id FROM T_Invoices 
JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
WHERE InvoiceDate Between %s AND %s AND Party_id=%s AND  TC_InvoiceItems.Item_id=%s

UNION ALL

SELECT 5 Sequence, T_PurchaseReturn.ReturnDate TransactionDate,T_PurchaseReturn.CreatedOn,
T_PurchaseReturn.FullReturnNumber TransactionNumber,M_Parties.Name,
UnitwiseQuantityConversion({Item},Quantity,TC_PurchaseReturnItems.Unit_id,0,0,{Unit},0)Quantity,TC_PurchaseReturnItems.Unit_id FROM T_PurchaseReturn 
JOIN TC_PurchaseReturnItems ON TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
JOIN M_Parties ON M_Parties.id = T_PurchaseReturn.Party_id
WHERE ReturnDate Between %s AND %s AND Customer_id=%s AND TC_PurchaseReturnItems.Item_id=%s and ((TC_PurchaseReturnItems.ItemReason_id IN (SELECT DefaultValue FROM M_Settings WHERE id = 14) and T_PurchaseReturn.Mode =3) OR(T_PurchaseReturn.Mode =2))
                                                     
UNION ALL

select 7 Sequence,ProductionDate TransactionDate,T_Production.CreatedOn,
T_Production.FullProductionNumber TransactionNumber,M_Parties.Name,
UnitwiseQuantityConversion({Item},ActualQuantity,T_Production.Unit_id,0,0,{Unit},0)Quantity,T_Production.Unit_id
 from T_Production 
 JOIN M_Parties ON M_Parties.id = T_Production.Division_id
 where ProductionDate Between %s AND %s AND Division_id ={Party}  and Item_id={Item}
 
union all
 
select 8 Sequence ,C.ChallanDate TransactionDate,C.CreatedOn,C.FullChallanNumber TransactionNumber,
M_Parties.Name,UnitwiseQuantityConversion({Item},CI.Quantity,CI.Unit_id,0,0,{Unit},0)Quantity ,CI.Unit_id
 from T_Challan C
 join TC_ChallanItems CI on C.id=CI.Challan_id
 JOIN M_Parties ON M_Parties.id = C.Party_id
 where C.ChallanDate Between %s AND %s AND C.Party_id={Party}  and Item_id={Item}
 
union all
 
SELECT 9 Sequence, T_GRNs.GRNDate TransactionDate,T_GRNs.CreatedOn,T_GRNs.FullGRNNumber TransactionNumber,
M_Parties.Name,UnitwiseQuantityConversion({Item},Quantity,TC_GRNItems.Unit_id,0,0,{Unit},0)Quantity,TC_GRNItems.Unit_id FROM T_GRNs 
 JOIN TC_GRNItems ON TC_GRNItems.GRN_id=T_GRNs.id
 JOIN M_Parties ON M_Parties.id = T_GRNs.Party_id
 WHERE GRNDate Between %s AND %s AND Customer_id={Party} and TC_GRNItems.Item_id={Item} and T_GRNs.IsGRNType=0

 union all

select 10 Sequence,MI.MaterialIssueDate TransactionDate,MI.CreatedOn,MI.FullMaterialIssueNumber TransactionNumber,
M_Parties.Name,UnitwiseQuantityConversion({Item},MII.IssueQuantity,MII.Unit_id,0,0,{Unit},0)Quantity,MII.Unit_id
from T_MaterialIssue MI 
join TC_MaterialIssueItems MII on MII.MaterialIssue_id=MI.id
JOIN M_Parties ON M_Parties.id = MI.Party_id
where MI.MaterialIssueDate Between %s AND %s and Party_id={Party} and MII.Item_id={Item}                                                                                                         
                                                     
                                )a  order by TransactionDate, CreatedOn ''', ([FromDate, ToDate, Party, Item,  FromDate, ToDate, Party, Item, DefaultValues,  FromDate, ToDate, Party, Item,  FromDate, ToDate, Party, Item, FromDate, ToDate, Party, Item,FromDate, ToDate, Party, Item, FromDate, ToDate, FromDate, ToDate, FromDate, ToDate, FromDate, ToDate]))
                # print(query)
                if query:
                    MaterialRegisterList = MaterialRegisterSerializerView(
                        query, many=True).data
                    query2 = O_DateWiseLiveStock.objects.filter(
                        StockDate=FromDate, Party=Party, Item=Item).values('OpeningBalance', 'Unit_id')

                    if query2:

                        # if int(query2[0]['OpeningBalance']) > 0:
                        OpeningBalance = UnitwiseQuantityConversion(
                            Item, query2[0]['OpeningBalance'], 0, query2[0]['Unit_id'], 0, Unit, 0).ConvertintoSelectedUnit()
                    else:

                        OpeningBalance = 0.00

                    query3 = O_DateWiseLiveStock.objects.filter(
                        StockDate=ToDate, Party=Party, Item=Item).values('ClosingBalance', 'Unit_id')

                    if query3:

                        ClosingBalance = UnitwiseQuantityConversion(
                            Item, query3[0]['ClosingBalance'], 0, query3[0]['Unit_id'], 0, Unit, 0).ConvertintoSelectedUnit()

                    else:
                        ClosingBalance = 0.00
                        # log_entry = create_transaction_logNew(request,Reportdata,Party,'Stock Processing Needed',215,0,FromDate,ToDate,0)
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Stock Processing Needed', 'Data': []})
                    MaterialRegisterList.append(
                        {"OpeningBalance": OpeningBalance, "ClosingBalance": ClosingBalance,"UnitName":UnitName})
                    log_entry = create_transaction_logNew(request, Reportdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 215, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialRegisterList})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, Party, 'Records Not available', 215, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'MaterialRegister:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class CreditDebitExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Customer = Reportdata['Customer']
                NoteTypeIDs = Reportdata['NoteTypeIDs']
                NoteType_list = NoteTypeIDs.split(",")

                if(Party) > 0:
                    query = TC_CreditDebitNoteItems.objects.raw('''SELECT TC_CreditDebitNoteItems.id,T_CreditDebitNotes.Party_id AS SupplierID,A.Name SupplierName,T_CreditDebitNotes.FullNoteNumber AS InvoiceNumber,T_CreditDebitNotes.CRDRNoteDate AS InvoiceDate,T_CreditDebitNotes.Narration,C.Name As NoteTypeName , D.Name As NoteReasonName,T_CreditDebitNotes.Customer_id As CustomerID,B.Name CustomerName,TC_CreditDebitNoteItems.Item_id As FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_CreditDebitNoteItems.MRPValue , TC_CreditDebitNoteItems.QtyInNo, TC_CreditDebitNoteItems.QtyInKg,TC_CreditDebitNoteItems.QtyInBox, "" AS RatePerPiece,TC_CreditDebitNoteItems.Rate AS BasicRate, (TC_CreditDebitNoteItems.Rate +((TC_CreditDebitNoteItems.Rate * TC_CreditDebitNoteItems.GSTPercentage)/100))WithGSTRate,M_Units.Name AS UnitName,TC_CreditDebitNoteItems.DiscountType, TC_CreditDebitNoteItems.Discount, TC_CreditDebitNoteItems.DiscountAmount,TC_CreditDebitNoteItems.BasicAmount AS TaxableValue, TC_CreditDebitNoteItems.CGSTPercentage, TC_CreditDebitNoteItems.CGST,TC_CreditDebitNoteItems.SGSTPercentage, TC_CreditDebitNoteItems.SGST,TC_CreditDebitNoteItems.IGSTPercentage,TC_CreditDebitNoteItems.IGST,TC_CreditDebitNoteItems.GSTPercentage, TC_CreditDebitNoteItems.Amount AS TotalValue, T_CreditDebitNotes.RoundOffAmount,T_CreditDebitNotes.GrandTotal,M_Routes.Name AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_CreditDebitNoteUploads.Irn, TC_CreditDebitNoteUploads.AckNo,TC_CreditDebitNoteUploads.EwayBillNo
FROM TC_CreditDebitNoteItems
JOIN T_CreditDebitNotes ON T_CreditDebitNotes.id=TC_CreditDebitNoteItems.CRDRNote_id
JOIN M_Parties A ON A.id= T_CreditDebitNotes.Party_id
JOIN M_Parties B ON B.id = T_CreditDebitNotes.Customer_id
JOIN M_States ON M_States.id = B.State_id
JOIN M_Items ON M_Items.id = TC_CreditDebitNoteItems.Item_id
JOIN C_Companies ON C_Companies.id = M_Items.Company_id
JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_CreditDebitNoteItems.Unit_id
JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_CreditDebitNoteItems.GST_id
JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_CreditDebitNotes.Customer_id AND MC_PartySubParty.Party_id=%s
LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN TC_CreditDebitNoteUploads ON TC_CreditDebitNoteUploads.CRDRNote_id=T_CreditDebitNotes.id
JOIN M_GeneralMaster C ON C.id = T_CreditDebitNotes.NoteType_id
LEFT JOIN M_GeneralMaster D ON D.id = T_CreditDebitNotes.NoteReason_id

WHERE T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND T_CreditDebitNotes.Party_id=%s AND T_CreditDebitNotes.IsDeleted=0 AND NoteType_id IN %s ''', ([Party], [FromDate], [ToDate], [Party], NoteType_list))
                # CustomPrint(query.query)
                if query:
                    InvoiceExportData = list()
                    InvoiceExportSerializer = CreditDebitDataExportSerializer(
                        query, many=True).data
                    for b in InvoiceExportSerializer:

                        qur2 = M_Parties.objects.filter(
                            id=b['CustomerID']).values('PriceList').distinct()
                        query = M_PriceList.objects.values(
                            'id').filter(id__in=qur2)
                        Rate = RateCalculationFunction(
                            0, b['FE2MaterialID'], 0, 0, 1, 0, query[0]['id']).RateWithGST()
                        NoRate = float(Rate[0]['NoRatewithOutGST'])
                        InvoiceExportData.append({

                            "SupplierID": b['SupplierID'],
                            "SupplierName": b['SupplierName'],
                            "InvoiceNumber": b['InvoiceNumber'],
                            "InvoiceDate": b['InvoiceDate'],
                            "Narration": b['Narration'],
                            "NoteType": b['NoteTypeName'],
                            "NoteReason": b['NoteReasonName'],
                            "CustomerID": b['CustomerID'],
                            "CustomerName": b['CustomerName'],
                            "FE2MaterialID": b['FE2MaterialID'],
                            "MaterialName": b['MaterialName'],
                            "CompanyName": b['CompanyName'],
                            "HSNCode": b['HSNCode'],
                            "MRP": b['MRPValue'],
                            "QtyInNo": b['QtyInNo'],
                            "QtyInKg": b['QtyInKg'],
                            "QtyInBox": b['QtyInBox'],
                            "BasicRate": b['BasicRate'],
                            "WithGSTRate": b['WithGSTRate'],
                            "NoRate": NoRate,
                            "UnitName": b['UnitName'],
                            "DiscountType": b['DiscountType'],
                            "Discount": b['Discount'],
                            "DiscountAmount": b['DiscountAmount'],
                            "TaxableValue": b['TaxableValue'],
                            "CGST": b['CGST'],
                            "CGSTPercentage": b['CGSTPercentage'],
                            "SGST": b['SGST'],
                            "SGSTPercentage": b['SGSTPercentage'],
                            "IGST": b['IGST'],
                            "IGSTPercentage": b['IGSTPercentage'],
                            "GSTPercentage": b['GSTPercentage'],
                            "GSTAmount": b['GSTAmount'],
                            "TotalValue": b['TotalValue'],
                            # "TCSAmount":b['TCSAmount'],
                            "RoundOffAmount": b['RoundOffAmount'],
                            "GrandTotal": b['GrandTotal'],
                            "RouteName": b['RouteName'],
                            "StateName": b['StateName'],
                            "GSTIN": b['GSTIN'],
                            "Irn": b['Irn'],
                            "AckNo": b['AckNo'],
                            "EwayBillNo": b['EwayBillNo'],
                        })
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'From:'+str(FromDate)+'To:'+str(ToDate), 216, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceExportData})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'Report Not available', 216, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'CreditDebitExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ReceiptDataExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']

                if(Party) > 0:
                    query = T_Receipts.objects.raw(
                        '''SELECT T_Receipts.id, T_Receipts.Party_id AS SupplierID, A.Name SupplierName, T_Receipts.FullReceiptNumber AS ReceiptNumber, T_Receipts.ReceiptDate, T_Receipts.Customer_id AS CustomerID,B.Name CustomerName,C.Name As ReceiptTypeName,D.Name As ReceiptModeName,E.Name As BankName,F.Name As DepositorBankName,AmountPaid,T_Receipts.Description,ChequeDate,DocumentNo FROM T_Receipts JOIN  M_GeneralMaster C ON C.id=T_Receipts.ReceiptType_id JOIN  M_GeneralMaster D ON D.id=T_Receipts.ReceiptMode_id LEFT JOIN M_Bank E ON E.id=T_Receipts.Bank_id LEFT JOIN M_Bank F ON F.id=T_Receipts.DepositorBank_id JOIN M_Parties A on A.id= T_Receipts.Party_id JOIN M_Parties B on B.id = T_Receipts.Customer_id WHERE T_Receipts.ReceiptDate BETWEEN %s AND %s AND T_Receipts.Party_id=%s Order By id desc''', ([FromDate], [ToDate], [Party]))
                # CustomPrint(query.query)
                if query:
                    ReceiptExportData = list()
                    ReceiptExportSerializer = ReceiptDataExportSerializer(
                        query, many=True).data
                    for b in ReceiptExportSerializer:
                        ReceiptExportData.append({
                            "id": b['id'],
                            "SupplierID": b['SupplierID'],
                            "SupplierName": b['SupplierName'],
                            "ReceiptNumber": b['ReceiptNumber'],
                            "ReceiptDate": b['ReceiptDate'],
                            "CustomerID": b['CustomerID'],
                            "CustomerName": b['CustomerName'],
                            "ReceiptType": b['ReceiptTypeName'],
                            "ReceiptMode": b['ReceiptModeName'],
                            "BankName": b['BankName'],
                            "DepositorBankName": b['DepositorBankName'],
                            "AmountPaid": b['AmountPaid'],
                            "Description": b['Description'],
                            "ChequeDate": b['ChequeDate'],
                            "DocumentNo": b['DocumentNo']
                        })
                    log_entry = create_transaction_logNew(request, Reportdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 217, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReceiptExportData})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, Party, 'Report Not available', 217, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'ReceiptDataExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


class OutStandingBalanceView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Balance_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = Balance_Data['PartyID']
                Route = Balance_Data['RouteID']
                ToDate = Balance_Data['Date']

                if Route == '':
                    query = MC_PartySubParty.objects.raw('''SELECT M_Parties.id, M_Parties.Name AS PartyName, M_Routes.Name AS RouteName
FROM MC_PartySubParty
JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id
LEFT JOIN M_Routes ON M_Routes.id = MC_PartySubParty.Route_id WHERE MC_PartySubParty.Party_id = %s''', ([Party]))

                else:
                    query = MC_PartySubParty.objects.raw('''SELECT M_Parties.id, M_Parties.Name AS PartyName, M_Routes.Name AS RouteName
FROM MC_PartySubParty
JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id
LEFT JOIN M_Routes ON M_Routes.id = MC_PartySubParty.Route_id WHERE MC_PartySubParty.Party_id = %s AND MC_PartySubParty.Route_id = %s''', ([Party], [Route]))
                if query:
                    Balance_Serializer = BalanceSerializer(
                        query, many=True).data
                    BalanceList = list()

                    for a in Balance_Serializer:
                        BalanceList.append({
                            "PartyID": a['id'],
                            "PartyName": a['PartyName'],
                            "RouteName": a['RouteName'],
                            "OutStandingBalance": round(float(GetOpeningBalance(Party, a['id'], ToDate)), 2)
                        })
                    log_entry = create_transaction_logNew(request, Balance_Data, Party, 'To:'+str(ToDate), 218, 0, 0, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BalanceList})
                log_entry = create_transaction_logNew(request, Balance_Data, Party, 'Report Not Found', 218, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Balance_Data, 0, 'OutStandingBalanceReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ManPowerReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,EmployeeID=0):
        try:
            with transaction.atomic():
                EmpPartys=MC_EmployeeParties.objects.raw('''select EmployeeParties(%s) id''',[EmployeeID])
                for row in EmpPartys:
                    p=row.id
                PartyIDs = p.split(",")
                
                query = MC_PartySubParty.objects.raw(f'''SELECT  MC_PartySubParty.id,A.SAPPartyCode AS SAPCode, 
A.id AS FEParty_id, A.NAME AS PartyName,  A.isActive AS PartyActive, A.CreatedOn AS PartyCreation,
M_PartyType.Name AS PartyType, A.Email, A.PAN, MC_PartySubParty.Party_id AS SS_id, B.NAME AS SSName, M_Users.LoginName AS LoginID,
"India" AS country, C.Address, M_States.Name AS State, M_Districts.Name AS District, A.ClosingDate AS PartyClosingDate,
M_Cities.Name AS City, C.PIN AS PIN, A.MobileNo AS Mobile, M_Employees.Name AS OwnerName,
A.Latitude, A.Longitude, C.FSSAINo AS FSSAINo, C.FSSAIExipry AS FSSAIExpiry, C.fssaidocumenturl, C.id AS PartyAddressID, A.GSTIN AS GSTIN, M_Employees_GM.Name AS GM, 
M_Employees_NH.Name AS NSM, M_Employees_RH.Name AS RSM, M_Employees_ASM.Name AS ASM,M_Employees_SE.Name AS SE,M_Employees_SO.Name AS SO,
M_Employees_SR.Name AS SR, M_Employees_MT.Name AS MT, M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
FROM MC_PartySubParty 
LEFT JOIN M_Parties A ON A.id = MC_PartySubParty.SubParty_id and A.id in %s
LEFT JOIN M_Parties B ON B.id = MC_PartySubParty.Party_id
LEFT JOIN M_PartyType ON M_PartyType.id = A.PartyType_id
LEFT JOIN MC_PartyAddress  C ON C.Party_id = A.id AND C.IsDefault = 1
LEFT JOIN M_States ON M_States.id = A.State_id
LEFT JOIN M_Districts ON M_Districts.id = A.District_id
LEFT JOIN M_Cities ON M_Cities.id = A.City_id
LEFT JOIN MC_EmployeeParties ON MC_EmployeeParties.Party_id = A.id 
LEFT JOIN M_Employees On M_Employees.id = MC_EmployeeParties.Employee_id
LEFT JOIN M_Users On M_Users.Employee_id = M_Employees.id and M_Users.POSRateType=0
LEFT JOIN M_PartyDetails X On  A.id=X.Party_id AND X.Group_id is null
LEFT JOIN M_Cluster On X.Cluster_id=M_Cluster.id
LEFT JOIN M_SubCluster On X.SubCluster_id=M_SubCluster.id
LEFT JOIN M_Employees M_Employees_GM ON M_Employees_GM.id = X.GM
LEFT JOIN M_Employees  M_Employees_NH ON M_Employees_NH.id = X.NH
LEFT JOIN M_Employees  M_Employees_RH ON M_Employees_RH.id = X.RH
LEFT JOIN M_Employees M_Employees_ASM ON M_Employees_ASM.id = X.ASM
LEFT JOIN M_Employees M_Employees_SE ON M_Employees_SE.id = X.SE
LEFT JOIN M_Employees M_Employees_SO ON M_Employees_SO.id = X.SO
LEFT JOIN M_Employees M_Employees_SR ON M_Employees_SR.id = X.SR
LEFT JOIN M_Employees M_Employees_MT ON M_Employees_MT.id = X.MT
                                                     
WHERE M_PartyType.id IN(9,10,15,17,19)  ''',[PartyIDs])
               
                if query:
                    # ManPower_Serializer = ManPowerSerializer(query, many=True).data
                    ManPowerList = list()
                    CustomPrint(query)
                    for a in query:
                        # PartyDateTime = datetime.strptime(str(a.PartyCreation), "%Y-%m-%dT %H:%M:%S.%f")
                        # PartyCreation = PartyDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        PartyDateTime = datetime.strptime(str(a.PartyCreation), "%Y-%m-%d %H:%M:%S.%f")
                        PartyCreation = PartyDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        ManPowerList.append({
                            "SAPCode": a.SAPCode,
                            "FEParty_id": a.FEParty_id,
                            "PartyName": a.PartyName,
                            "PartyActive": a.PartyActive,
                            "PartyCreation":PartyCreation,
                            "PartyClosingDate" : a.PartyClosingDate,
                            "PartyType": a.PartyType,
                            "Email": a.Email,
                            "PAN":a.PAN,
                            "SS_id": a.SS_id,
                            "SSName": a.SSName,
                            "LoginID": a.LoginID,
                            "country": a.country,
                            "Cluster" : a.Cluster,
                            "SubCluster": a.SubCluster,
                            "Address": a.Address,
                            "State": a.State,
                            "District": a.District,
                            "City": a.City,
                            "PIN": a.PIN,
                            "Mobile": a.Mobile,
                            "OwnerName": a.OwnerName,
                            "Latitude": a.Latitude,
                            "Longitude": a.Longitude,
                            "FSSAINo": a.FSSAINo,
                            "FSSAIExpiry": a.FSSAIExpiry,
                            "GSTIN": a.GSTIN,
                            "GM": a.GM,
                            "NSM": a.NSM,
                            "RSM": a.RSM,
                            "ASM": a.ASM,
                            "SE": a.SE,
                            "SO": a.SO,
                            "SR": a.SR,
                            "MT": a.MT,
                            "FSSAIDocument": f"{NewURLPrefix()}/downloadQr/{a.PartyAddressID}/4" if a.fssaidocumenturl else None,
                            "FSSAIDocumentFilename": get_uploaded_filename(DummyFile(a.fssaidocumenturl)) if a.fssaidocumenturl else None

                            
                            })
                    log_entry = create_transaction_logNew(request, query, 0, '', 219, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ManPowerList})
                log_entry = create_transaction_logNew(request, query, 0, 'Report Not Found', 219, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'ManPowerReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ProductAndMarginReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        data = JSONParser().parse(request)
        
        try:
            with transaction.atomic():
                today = date.today()
                IsSCM = data['IsSCM']
                PartyID = data['Party']
                PartyTypeID = data['PartyType'].split(",")
                PriceListID = data['PriceList']
                CompanyID = data['Company']
                GroupID = data['Group'].split(",")
                SubGroupID = data['SubGroup'].split(",")
                ItemID = data['Item'].split(",")
                PartyTypeID = [int(i) for i in PartyTypeID]
                try:
                    CompanyIDs=MC_EmployeeParties.objects.raw(f'''select GetAllCompanyIDsFromLoginCompany({CompanyID}) id''')
                    for row in CompanyIDs:
                        p=row.id
                    Party_ID = p.split(",")
                    dd=Party_ID[:-1]
                    C=', '.join(dd)
                    
                    if(PriceListID):
                        PriceListID = int(PriceListID)
                    else:
                        if len(PartyTypeID) > 0:
                            PartyTypeIDs = ','.join(map(str, PartyTypeID))
                            PriceListQuery=M_PriceList.objects.raw(f''' SELECT id,Name,ShortName AS  PLShortName,CalculationPath
                                                                      FROM M_PriceList 
                                                                      WHERE PLPartyType_id in({PartyTypeIDs}) and Company_id in( {C}) order by Sequence''')
                            
                            PriceListIDComma = [str(item.id) for item in PriceListQuery]
                            if PriceListIDComma:  
                                PriceListID = ','.join(PriceListIDComma)
                            else:
                                PriceListID = 0
                        else:
                            PriceListID = 0               
                except (ValueError, TypeError):
                    PriceListID = 0

                query =f""" SELECT M_Items.id ,SAPItemCode,BarCode,GSTHsnCodeMaster(M_Items.id,%s,3,{PartyID},0)HSNCode,C_Companies.Name CompanyName,isActive,
(case when Length ='' then '' else concat(Length,'L X ',Breadth,'B X ',Height,'W - MM') end)BoxSize,StoringCondition
,ifnull(M_Group.Name,'') Product,ifnull(MC_SubGroup.Name,'') SubProduct,M_Items.Name ItemName,ShortName AS ItemShortName,
round(GetTodaysDateMRP(M_Items.id,%s,2,0,{PartyID},0),0) MRP,round(GSTHsnCodeMaster(M_Items.id,%s,2,{PartyID},0),2)GST,M_Units.Name BaseUnit,Grammage SKUVol,
MC_ItemShelfLife.Days ShelfLife,PIB.BaseUnitQuantity PcsInBox , PIK.BaseUnitQuantity PcsInKg, PIN.BaseUnitQuantity PcsInNo, ifnull(M_Group.id,'') ProductID,ifnull(MC_SubGroup.id,'') SubProductID
 ,M_Items.BaseUnitID_id
 FROM M_Items
 join C_Companies on C_Companies.id=M_Items.Company_id 
 left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id = 1
 left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
 left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
 left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
 join M_Units on M_Units.id=M_Items.BaseUnitID_id
 left join MC_ItemShelfLife on MC_ItemShelfLife.Item_id=M_Items.id and IsDeleted=0
 JOIN MC_ItemUnits PIB on PIB.Item_id=M_Items.id and PIB.UnitID_id=4 and PIB.IsDeleted=0
 JOIN MC_ItemUnits PIK on PIK.Item_id=M_Items.id and PIK.UnitID_id=2 and PIK.IsDeleted=0
 JOIN MC_ItemUnits PIN on PIN.Item_id=M_Items.id and PIN.UnitID_id=1 and PIN.IsDeleted=0
 
 """
                q=C_Companies.objects.filter(id=CompanyID).values('IsSCM')
    
                if q[0]['IsSCM'] == 1:
                   
                    
                    Companycondition = f"where M_Items.Company_id in( {C}) and M_Items.IsSCM=1"
                else:
                    Companycondition = f"where M_Items.Company_id = {CompanyID}"
                
                if IsSCM == '0':
                    query += f"{Companycondition} "
                    # query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence  "
                    ItemQuery = M_Items.objects.raw(query, [today, today, today])
                else:
                    
                    query += f"join MC_PartyItems on MC_PartyItems.Item_id=M_Items.id and MC_PartyItems.Party_id=%s {Companycondition}"
                    # query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence  "
                    ItemQuery = M_Items.objects.raw(query, [today, today, today, PartyID])
                   
                if any(ItemID) :    
                    
                    query += " "
                    query += "  AND M_Items.id in %s "
                    query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence  "
                    
                    if IsSCM == '0':
                           
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,ItemID])
                        
                    else:
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,PartyID,ItemID])
                     
                elif any(SubGroupID):
                      
                    query += " "
                    query += "  AND M_Group.id in %s and MC_SubGroup.id in %s"
                    query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence"
                    if IsSCM == '0':
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,GroupID,SubGroupID])
                    else:
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,PartyID,GroupID,SubGroupID])
                elif any(GroupID):
                    
                    query += " "
                    query += "  AND M_Group.id in %s "
                    query += "order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence"
                    if IsSCM == '0':
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,GroupID])
                    else:
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,PartyID,GroupID])
                    
                ItemsList = list()
              
                if ItemQuery:    
                    for row in ItemQuery:
                        
                        if IsSCM == '0':
                           
                            if PriceListID == 0:
                                pricelistquery=M_PriceList.objects.raw(f'''SELECT id,Name,ShortName AS PLShortName FROM M_PriceList where Company_id in( {C})  order by Sequence''')
                            else:                               
                                all_ids = []
                                pricelistquery=M_PriceList.objects.raw(f'''SELECT id,Name,ShortName AS PLShortName,CalculationPath FROM M_PriceList where Company_id in( {C}) and id  in ({PriceListID}) order by Sequence''')                               
                                for i in pricelistquery:
                                    pp=(i.CalculationPath).split(',')  
                                    all_ids.extend(pp) 
                                    all_ids = list(set(all_ids))
                                    all_ids_tuple = tuple(all_ids)
                                    pricelistquery=M_PriceList.objects.raw('''SELECT id,Name,ShortName AS PLShortName FROM M_PriceList where id in %s order by Sequence''',[all_ids_tuple])
                               
                        else:
                            if PriceListID == 0:
                                pricelistquery=M_PriceList.objects.raw('''select distinct PriceList_id id,M_PriceList.Name,M_PriceList.CalculationPath,M_PriceList.ShortName AS PLShortName from M_Parties 
join MC_PartySubParty on MC_PartySubParty.SubParty_id=M_Parties.id 
join M_PriceList on M_PriceList.id=M_Parties.PriceList_id
where  M_Parties.id=%s or MC_PartySubParty.Party_id=%s ''',(PartyID,PartyID))
                
                            else:
                                all_ids = []
                                pricelistquery=M_PriceList.objects.raw('''select distinct PriceList_id id,M_PriceList.Name,M_PriceList.CalculationPath,M_PriceList.ShortName AS PLShortName from M_Parties 
join MC_PartySubParty on MC_PartySubParty.SubParty_id=M_Parties.id 
join M_PriceList on M_PriceList.id=M_Parties.PriceList_id
where  M_Parties.id=%s or MC_PartySubParty.Party_id=%s and M_PriceList.id in (%s) ''',(PartyID,PartyID,PriceListID))
                                for i in pricelistquery:
                                    
                                    pp=(i.CalculationPath).split(',')
                                    all_ids.extend(pp) 
                                    all_ids = list(set(all_ids))
                                    all_ids_tuple = tuple(all_ids)
                                    pricelistquery=M_PriceList.objects.raw('''SELECT id,Name,ShortName AS PLShortName,CalculationPath FROM M_PriceList where id in %s order by Sequence''',[all_ids_tuple])
              
                        ItemMargins = list()
                        RateList = list()
                        ItemImage = list()
                        PartyTypeMRP =list()
                        for x in pricelistquery:
                            
                            query2 = M_MarginMaster.objects.raw('''select 1 as id, GetTodaysDateMargin(%s,%s,%s,0,0)Margin,RateCalculationFunction1(0, %s, 0, 1, 0, %s, 0, 0)RatewithoutGST,RateCalculationFunction1(0, %s, 0, 1, 0, %s, 0, 1)RatewithGST,RateCalculationFunction1(0, %s, 0, %s, 0, %s, 0, 0)BaseUnitRatewithoutGST''', (
                                row.id, today, x.id, row.id, x.id, row.id, x.id,row.id, row.BaseUnitID_id,x.id))

                            for a in query2:
                                # string1 = x['Name']
                                # string2 = x['ShortName'].replace(" ","")
                                string2 = (x.Name).replace(" ", "")
                                ItemMargins.append({
                                    string2+'Margin': str(float(a.Margin)) + '%'
                                })
                                RateList.append({

                                    string2+'RateWithGST': float(a.RatewithGST),
                                    string2+'RateWithOutGST': float(a.RatewithoutGST),
                                    string2+'BaseUnitRateWithOutGST': float(a.BaseUnitRatewithoutGST),
                                    "PriceListID" : x.id

                                })
                           
                        # MRPQuery = M_MRPMaster.objects.raw(f'''
                        #     SELECT mm.id, mm.MRP,  pt.Name AS PartyTypeName
                        #     FROM M_MRPMaster mm
                        #     JOIN M_PartyType pt ON pt.id = mm.PartyType_id
                        #     JOIN (
                        #         SELECT Item_id, PartyType_id, MAX(EffectiveDate) AS MaxDate
                        #         FROM M_MRPMaster
                        #         WHERE Item_id IN ({row.id}) AND IsDeleted = 0
                        #         GROUP BY Item_id, PartyType_id
                        #     ) latest ON latest.Item_id = mm.Item_id 
                        #             AND latest.PartyType_id = mm.PartyType_id 
                        #             AND latest.MaxDate = mm.EffectiveDate
                        #     WHERE mm.IsDeleted = 0''')
                        # PartyTypequery=M_Parties.objects.raw(f'''Select M_Parties.id, PartyType_id From M_Parties where id={PartyID}''')
                        # PartyTypeID = PartyTypequery[0].PartyType_id
                        # party_type = M_PartyType.objects.get(id=PartyTypeID)
                        # MRPQuery = M_MRPMaster.objects.raw(f'''Select GetTodaysDateMRP({row.id},CURDATE(),1,0,0,{PartyTypeID}) id,GetTodaysDateMRP({row.id},CURDATE(),1,0,0,{PartyTypeID}) MRP''')
                        PartyTypequery=M_MRPMaster.objects.raw(f'''Select id ,PartyType_id ,Max(EffectiveDate) from M_MRPMaster where Item_id in({row.id}) and PartyType_id is not null  group by PartyType_id ''')
                        PartyTypeMRP = []
                        for pt in PartyTypequery:
                            PartyTypeID = pt.PartyType_id
                            party_type = M_PartyType.objects.get(id=PartyTypeID)
                            
                            MRPQuery = M_MRPMaster.objects.raw(f'''
                                SELECT GetTodaysDateMRP({row.id}, CURDATE(), 1, 0, 0, {PartyTypeID}) AS id,
                                    GetTodaysDateMRP({row.id}, CURDATE(), 2, 0, 0, {PartyTypeID}) AS MRP,GSTHsnCodeMaster({row.id},CURDATE(),2,0, {PartyTypeID})GST
                            ''')                        
                            if MRPQuery:
                                for row1 in MRPQuery:               
                                        rec = MRPQuery[0]
                                        PartyTypeMRP.append({
                                            f'{party_type.Name}MRP': float(rec.MRP),
                                            f'{party_type.Name}GST%': f"{float(rec.GST)}%"
                                        })
                        ww =PartyTypeMRP+ItemMargins+RateList
                        query3 = MC_ItemImages.objects.raw(
                            '''select %s as id,M_ImageTypes.name ImageTypeName,M_ImageTypes.id ImageTypeid,ifnull(MC_ItemImages.Item_pic,' ')Item_pic from MC_ItemImages right join M_ImageTypes on M_ImageTypes.id=MC_ItemImages.ImageType_id and MC_ItemImages.Item_id=%s''', (row.id, row.id))
                        for b in query3:
                            ItemImage.append({
                                b.ImageTypeName: str(b.Item_pic)

                            })
                        ItemsList.append({

                            "FE2ItemID": row.id,
                            "SAPCode": row.SAPItemCode,
                            "Barcode": row.BarCode,
                            "HSNCode": '`'+ row.HSNCode,
                            "Company": row.CompanyName,
                            "SKUStatus(T,F)": row.isActive,
                            "BoxSize": row.BoxSize,
                            "StoringCondition": row.StoringCondition,
                            "Product": row.Product,
                            "SubProduct": row.SubProduct,
                            "SKUName": row.ItemName,
                            "SKUShortName": row.ItemShortName,
                            "MRP": row.MRP,
                            "GST%": str(row.GST) +'%',
                            "BaseUnit": row.BaseUnit,
                            "SKUVol": (row.SKUVol),
                            "ShelfLife": row.ShelfLife,
                            "PcsInBox": float(row.PcsInBox),
                            "PcsInKG": float(row.PcsInKg),
                            "PcsInNo": float(row.PcsInNo),
                            "ProductID" : row.ProductID,
                            "SubProductID" :row.SubProductID,
                            "ItemMargins": ww,
                            "ItemImage": ItemImage

                        })
                    log_entry = create_transaction_logNew(request, ItemsList, 0, '', 106, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemsList})
                log_entry = create_transaction_logNew(request, ItemsList, 0, "Report Not Available", 106, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Item Not Available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0, 'ProductAndMarginReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data': []})


#             SELECT M_Items.id FE2ItemID,SAPItemCode,BarCode,GSTHsnCodeMaster(M_Items.id,'2023-12-05',3,0,0)HSNCode,C_Companies.Name Company,isActive,
# (case when Length ='' then '' else concat(Length,'L X ',Breadth,'B X ',Height,'W - MM') end)BoxSize,StoringCondition
# ,ifnull(M_Group.Name,'') Product,ifnull(MC_SubGroup.Name,'') SubProduct,M_Items.Name ItemName,ShortName,
# round(GetTodaysDateMRP(M_Items.id,'2023-12-05',2,0,0,0),0) MRP,concat(round(GSTHsnCodeMaster(M_Items.id,'2023-12-05',2,0,0),2),'%')GST,M_Units.Name BaseUnit,Grammage SKUVol,
# MC_ItemShelfLife.Days ShelfLife,PIB.BaseUnitQuantity PcsInBox , PIK.BaseUnitQuantity PcsInKg
#  FROM M_Items
#  join C_Companies on C_Companies.id=M_Items.Company_id
#  left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
#  left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
#  left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id
#  left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
#  join M_Units on M_Units.id=M_Items.BaseUnitID_id
#  left join MC_ItemShelfLife on MC_ItemShelfLife.Item_id=M_Items.id
#  join MC_ItemUnits PIB on PIB.Item_id=M_Items.id and PIB.UnitID_id=4 and PIB.IsDeleted=0
#  join MC_ItemUnits PIK on PIK.Item_id=M_Items.id and PIK.UnitID_id=2 and PIK.IsDeleted=0

#  where MC_ItemGroupDetails.GroupType_id=1 order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence
#  limit 50;


class TCSAmountReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        TCSAmountData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = TCSAmountData['FromDate']
                ToDate = TCSAmountData['ToDate']
                Party = TCSAmountData['Party']

                if Party == "":
                    query = T_Invoices.objects.raw('''Select T_Invoices.id, T_Invoices.InvoiceDate, T_Invoices.InvoiceNumber, T_Invoices.TCSAmount AS TCSTaxAmount, T_Invoices.GrandTotal AS Total , M_Parties.id AS PartyID, M_Parties.Name AS PartyName From T_Invoices
Join M_Parties on T_Invoices.Party_id = M_Parties.id
WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.TCSAmount > 0''',(FromDate,ToDate))
                    log_entry = create_transaction_logNew(request, TCSAmountData, 0, '',266, 0)

                else:                                   
                    query = T_Invoices.objects.raw('''Select T_Invoices.id, T_Invoices.InvoiceDate, T_Invoices.InvoiceNumber, T_Invoices.TCSAmount AS TCSTaxAmount, T_Invoices.GrandTotal AS Total , M_Parties.id AS PartyID, M_Parties.Name AS PartyName
From T_Invoices
Join M_Parties on T_Invoices.Party_id = M_Parties.id
WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.TCSAmount > 0 AND T_Invoices.Party_id =%s''',(FromDate,ToDate,Party))
                    log_entry = create_transaction_logNew(request, TCSAmountData, Party, '',266, 0)
                    
                TSCAMountList = list()
                TCSAmountSerializer = TCSAmountReportSerializer(query,many=True).data         

                for a in TCSAmountSerializer:
                    GrandTotal = float(a['Total']) - float(a['TCSTaxAmount'])
                    TSCAMountList.append({
                        "InvoiceDate": a['InvoiceDate'],
                        "InvoiceNumber": a['InvoiceNumber'],
                        "GrandTotal": GrandTotal,
                        "TCSTaxAmount": a['TCSTaxAmount'],
                        "Total": a['Total'],
                        "PartyID":a['PartyID'],
                        "PartyName":a['PartyName']
                    })
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TSCAMountList})
        except Exception as e:
            log_entry = create_transaction_logNew(request, TCSAmountData, 0,'TCSAmountReport:'+str(e),33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

class CxDDDiffReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data['Party']
                InvoiceData=list()
                
                query='''select M_Parties.id,M_Parties.Name CXName,M_Items.Name ItemName,TC_InvoiceItems.MRPValue,sum(TC_InvoiceItems.Quantity)Quantity,M_Units.Name UnitName,TC_InvoiceItems.Rate,
IFNULL(RateCalculationFunction1(0, TC_InvoiceItems.Item_id, 0, M_Units.id, 0, 2, TC_InvoiceItems.MRPValue, 0),0)DDRate,S.Name SupplierName
from T_Invoices 
join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
join M_Parties on M_Parties.id=T_Invoices.Customer_id and M_Parties.PartyType_id=15
join M_Parties S on S.id=T_Invoices.Party_id 
join M_Items on M_Items.id=TC_InvoiceItems.Item_id
join MC_ItemUnits on MC_ItemUnits.id=TC_InvoiceItems.Unit_id
join M_Units on M_Units.id =MC_ItemUnits.UnitID_id
where T_Invoices.InvoiceDate between %s and %s 
 '''
                
                if Party > 0:
                    query += " and Party_id=%s"

                query += " group by M_Parties.id,TC_InvoiceItems.Item_id ,TC_InvoiceItems.MRPValue,TC_InvoiceItems.Unit_id,TC_InvoiceItems.Rate "   
          
                if Party > 0:
                    RateDiffQuery= T_Invoices.objects.raw(query, [FromDate,ToDate,Party])
                else:
                    RateDiffQuery= T_Invoices.objects.raw(query, [FromDate,ToDate])
                
                # CustomPrint(RateDiffQuery.query)
                if RateDiffQuery:
                    for row in RateDiffQuery:
                        diff=row.Rate-row.DDRate
                        InvoiceData.append({
                            "XpressName" : row.CXName,
                            "ItemName" : row.ItemName,
                            "MRP" : row.MRPValue,
                            "Quantity" : row.Quantity,
                            "Unit" :row.UnitName,
                            "CXRate" : row.Rate,
                            "DDRate" :row.DDRate,
                            "Diff" : round(diff,2),
                            "SumofDiff" : round(diff*row.Quantity,2),
                            "SupplierName" : row.SupplierName
                        })
                        log_entry = create_transaction_logNew(request, Data, Party, '', 366, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceData})
                else:
                    log_entry = create_transaction_logNew(request, Data, 0, "Report Not Available", 366, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not Available', 'Data': []})      
        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, 'CxDDDiffReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class FranchiseSecondarySaleReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data['Party']
                Item = Data['Item']

                # Invoicequery = '''Select T_Invoices.id, M_Parties.Name FranchiseName, M_Parties.SAPPartyCode SAPCode, M_Parties.Name SAPName, T_Invoices.InvoiceDate SaleDate, 
                #         0 ClientID, M_Items.CItemID CItemID, T_Invoices.FullInvoiceNumber BillNumber, M_Items.Name ItemName, A.Quantity, M_Units.Name UnitName,
                #         A.Rate, A.Amount,  M_Parties.MobileNo, M_Items.SAPItemCode MaterialSAPCode,M_Items.IsCBMItem
                #         from T_Invoices
                #         join TC_InvoiceItems A on A.Invoice_id = T_Invoices.id 
                #         join M_Parties on M_Parties.id = T_Invoices.Party_id
                #         join M_Items  on M_Items.id = A.Item_id
                #         join MC_ItemUnits on MC_ItemUnits.id = A.Unit_id
                #         join M_Units on M_Units.id = MC_ItemUnits.UnitID_id
                #         where T_Invoices.InvoiceDate between %s and %s '''
                
                SPOSInvoicequery ='''Select X.id, M_Parties.Name FranchiseName, M_Parties.SAPPartyCode SAPCode, M_Parties.Name SAPName, 
                                X.InvoiceDate SaleDate, X.ClientID, M_Items.id CItemID, X.FullInvoiceNumber BillNumber, M_Items.Name ItemName, 
                                Y.Quantity, M_Units.Name UnitName, Y.MRPValue Rate, Y.Amount, M_Items.IsCBMItem, X.MobileNo, 
                                M_Items.SAPItemCode MaterialSAPCode,Y.QtyInNo,Y.QtyInKg, Y.GSTPercentage, Y.BasicAmount,
                                Y.HSNCode,X.VoucherCode, X.CreatedOn, U.LoginName
                        from SweetPOS.T_SPOSInvoices X
                        join SweetPOS.TC_SPOSInvoiceItems Y on Y.Invoice_id = X.id 
                        join FoodERP.M_Parties on M_Parties.id = X.Party
                        join FoodERP.M_Items  on M_Items.id = Y.Item 
                        join FoodERP.MC_ItemUnits on MC_ItemUnits.id = Y.Unit
                        join FoodERP.M_Units on M_Units.id = MC_ItemUnits.UnitID_id
                        LEFT JOIN FoodERP.M_Users U ON U.id = X.CreatedBy
                        where X.InvoiceDate between %s and %s and X.IsDeleted=0  '''
                
                parameters = [FromDate,ToDate]
                if int(Party) > 0 and int(Item) > 0: 
                    # Invoicequery += ' AND T_Invoices.Party_id = %s AND A.Item_id = %s'
                    SPOSInvoicequery += ' AND X.Party = %s AND Y.Item = %s'
                    parameters.extend([Party, Item])

                elif int(Party) > 0:
                    # Invoicequery += ' AND A.Item_id = %s'
                    SPOSInvoicequery += ' AND X.Party = %s'
                    parameters.append(Party)

                elif int(Item) > 0:
                    
                    # Invoicequery += 'AND T_Invoices.Party_id = %s'
                    SPOSInvoicequery += 'AND Y.Item = %s'
                    parameters.append(Item)
                    
                # q1 = T_Invoices.objects.raw(Invoicequery,parameters)
                q2 = T_SPOSInvoices.objects.using('sweetpos_db').raw(SPOSInvoicequery,parameters)
                # combined_sale = list(q1) + list(q2)
                combined_sale =  list(q2)

                if combined_sale:
                    
                    ReportdataList = []
                    for a in combined_sale:      
                        if a.IsCBMItem == 1:
                            aa="Yes"
                        else:
                            aa= "No"
                        ReportdataList.append({
                        "id":a.id,
                        "FranchiseName": a.FranchiseName,
                        "SAPCode": a.SAPCode,
                        "SAPName": a.SAPName,
                        "SaleDate": a.SaleDate,
                        "ClientID": a.ClientID,
                        "CItemID": a.CItemID,
                        "BillNumber": a.BillNumber,
                        "ItemName": a.ItemName,
                        "Quantity":round(float(a.Quantity),3),
                        "UnitName": a.UnitName,
                        "Rate": a.Rate,
                        "Amount": a.Amount,
                        "Amount":round(float(a.Amount),2),
                        "IsCBMItem": aa,
                        "MobileNo": a.MobileNo,
                        "MaterialSAPCode": a.MaterialSAPCode,
                        "QtyInNo":round(float(a.QtyInNo),3),
                        "QtyInKg":round(float(a.QtyInKg),3),
                        "GSTPercentage":round(float(a.GSTPercentage),2),
                        "BasicAmount":round(float(a.BasicAmount),2),
                        "HSNCode" : a.HSNCode,
                        "VoucherCode":a.VoucherCode,
                        "CreatedOn" : a.CreatedOn,
                        "CashierName": a.LoginName 
                        })
                    log_entry = create_transaction_logNew(request, Data, Party, '', 414, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReportdataList})  
                log_entry = create_transaction_logNew(request, Data, 0, "Data Not Available", 414, 0, FromDate, ToDate, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not Available', 'Data': []}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, 'FranchiseSaleReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class BillBookingReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data['Party']
                GRNData=list()
              
                BillBookingquery =TC_GRNItems.objects.raw(f'''SELECT  T_GRNs.id,GRNDate,FullGRNNumber ,Sum(TC_GRNItems.BasicAmount)BasicAmount, 
                Sum(TC_GRNItems.CGST)CGST,Sum(TC_GRNItems.SGST)SGST 
                ,M_Parties.Name ,Sum(TC_GRNItems.Amount)Amount FROM T_GRNs
                JOIN TC_GRNItems ON  TC_GRNItems.Grn_id =T_GRNs.id  
                JOIN M_Parties ON M_Parties.id= T_GRNs.Party_id
                WHERE IsSave=2 AND GrnDate Between '{FromDate}' and '{ToDate}' and T_GRNs.Customer_id={Party} group by TC_GRNItems.GRN_id ,M_Parties.Name ''')
                if BillBookingquery:                     
                    for row in BillBookingquery:                       
                        GRNData.append({
                            "id":row.id,
                            "GRNDate":row.GRNDate,
                            "BillNumber":row.FullGRNNumber,
                            "Debit":row.BasicAmount,
                            "CGST":row.CGST,
                            "SGST":row.SGST,
                            "SupplierName":row.Name,
                            "Credit":row.Amount                            
                        })                          
                      
                log_entry = create_transaction_logNew(request, Data, Party, '', 431, 0, FromDate, ToDate, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GRNData})  
            log_entry = create_transaction_logNew(request, Data, 0, "Data Not Available", 431, 0, FromDate, ToDate, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not Available', 'Data': []}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, 'BillBookingReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
        
        
class DemandVsSupplyReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']                
                Party = Data['Party']              
                unit = Data['Unit']
                OrderType =Data['OrderType']
                EmployeeID =Data['EmployeeID']
                DemandVsSupplyData = []                
                # print(FromDate,ToDate,Party)
                if Party==0:
                    party_result = MC_EmployeeParties.objects.filter(Employee_id=EmployeeID).values_list('Party_id', flat=True)
                    
                    if party_result:                       
                        PartyList = list(party_result)
                        Party = ','.join(str(p) for p in PartyList)                        
                    else:
                        Party = ""
                        return JsonResponse({'StatusCode': 204,'Status': False,'Message': "Party not assigned to this employee.",'Data': []})
                                    
                PartyDetails=""
                SupplierDetails=""
                CustomerDetails=""
                
                if OrderType=="Sales": # Sales Order                   
                
                    SupplierDetails = f"AND S.id in ({Party})" 
                     
                    CustomerDetails = f"AND C.id in ({Party})" 
                    
                    
                else:
                    PartyDetails = f"AND C.id in ({Party})" 
                   
                
                   
                    
                # DemandVsReportquery =TC_OrderItems.objects.raw(f'''SELECT ROW_NUMBER() OVER (ORDER BY A.PartyName, A.OrderDate) AS id,A.*,B.QtyInKg SupplyInKg, B.QtyInNo SupplyInNo 
                # FROM (
                # select M_Parties.Name PartyName, OrderDate, M_Items.Name ItemName, SUM(QtyInKg) QtyInKg, SUM(QtyInNo) QtyInNo FROM T_Orders 
                # JOIN TC_OrderItems on Order_id = T_Orders.id 
                # JOIN M_Parties ON Customer_id = M_Parties.id
                # JOIN M_Items ON Item_id = M_Items.id
                # WHERE IsDeleted = 0 AND OrderDate BETWEEN '{FromDate}' AND '{ToDate}'  {PartyDetails}
                # Group By M_Parties.Name, OrderDate, M_Items.Name) A
                # LEFT JOIN (
                # select M_Parties.Name PartyName, InvoiceDate, M_Items.Name ItemName, SUM(QtyInKg) QtyInKg, SUM(QtyInNo) QtyInNo FROM T_Invoices 
                # JOIN TC_InvoiceItems on Invoice_id = T_Invoices.id 
                # JOIN M_Parties ON Customer_id = M_Parties.id
                # JOIN M_Items ON Item_id = M_Items.id
                # WHERE InvoiceDate BETWEEN '{FromDate}' AND '{ToDate}'  {PartyDetails}
                # Group By M_Parties.Name, InvoiceDate, M_Items.Name) B
                # ON A.PartyName = B.PartyName AND A.OrderDate = B.InvoiceDate AND A.ItemName = B.ItemName
                # WHERE A.QtyInKg != B.QtyInKg Order By A.PartyName, OrderDate''')
                
#                 DemandVsReportquery =TC_OrderItems.objects.raw(f'''SELECT 
#     ROW_NUMBER() OVER (ORDER BY A.PartyName, A.OrderDate) AS id,
#     A.*, 
#     COALESCE(B.BaseUnitQuantity, 0) AS SupplyBaseUnitQuantity, 
    
# FROM (
#     SELECT 
#         C.id CustomerID,S.id PartyID,
#         C.Name AS CustomerName, 
#         S.Name AS PartyName,
#         OrderDate, 
#         M_Items.id ItemID,
#         M_Items.Name AS ItemName, 
#         sum(BaseUnitQuantity) as BaseUnitQuantity,
        
#     FROM T_Orders
#     JOIN TC_OrderItems ON Order_id = T_Orders.id
#     JOIN M_Parties C ON Customer_id = C.id
#     JOIN M_Parties S ON supplier_id=S.id
#     JOIN M_Items ON Item_id = M_Items.id
#     WHERE IsDeleted = 0 
#         AND OrderDate BETWEEN '{FromDate}' AND '{ToDate}'  {PartyDetails} {SupplierDetails} 
#     GROUP BY C.id,S.id, OrderDate, M_Items.Name
# ) A
# LEFT JOIN (
#     SELECT 
#         C.id CustomerID,S.id PartyID,
#         C.Name AS CustomerName, 
#         S.Name AS PartyName,
#         InvoiceDate, 
#         M_Items.id ItemID,
#         M_Items.Name AS ItemName, 
#         sum(BaseUnitQuantity) as BaseUnitQuantity,
        
#     FROM T_Invoices
#     JOIN TC_InvoiceItems ON Invoice_id = T_Invoices.id
#     JOIN M_Parties C ON Customer_id = C.id
#     JOIN M_Parties S ON Party_id=S.id
#     JOIN M_Items ON Item_id = M_Items.id
#     WHERE InvoiceDate BETWEEN '{FromDate}' AND '{ToDate}'  {PartyDetails} {CustomerDetails} 
#     GROUP BY C.id,S.id, InvoiceDate, M_Items.Name
# ) B
#     ON A.id = B.id 
#    AND A.OrderDate = B.InvoiceDate 
#    AND A.ItemID = B.ItemID
#  WHERE A.BaseUnitQuantity != COALESCE(B.BaseUnitQuantity, 0) 
# ORDER BY (CASE WHEN COALESCE(B.QtyInKg, 0) = 0 AND COALESCE(B.QtyInNo, 0) = 0 THEN 0 ELSE 1 END), A.PartyName, A.OrderDate''')

# Shruti code 
# WHERE A.QtyInKg != COALESCE(B.QtyInKg, 0) and (
#         ROUND(COALESCE(A.QtyInKg, 5), 5) <> ROUND(COALESCE(B.QtyInKg, 5), 5)
#        OR ROUND(COALESCE(A.QtyInNo, 5), 5) <> ROUND(COALESCE(B.QtyInNo, 5), 5))  
# ORDER BY (CASE WHEN COALESCE(B.QtyInKg, 0) = 0 AND COALESCE(B.QtyInNo, 0) = 0 THEN 0 ELSE 1 END), A.PartyName, A.OrderDate

# ======================================================================================================
                DemandVsReportquery =TC_OrderItems.objects.raw(f'''SELECT
    ROW_NUMBER() OVER (ORDER BY A.PartyName, A.OrderDate) AS id,
    A.*,
    UnitwiseQuantityConversion(A.ItemID,COALESCE(A.BaseUnitQuantity, 0),0,A.BaseUnitID,0,A.UnitID,1) Demand,
    UnitwiseQuantityConversion(B.ItemID,COALESCE(B.BaseUnitQuantity, 0),0,B.BaseUnitID,0,B.UnitID,1) Supply,
    M_Units.Name UnitName
    
FROM (
    SELECT
        C.id CustomerID,S.id PartyID,
        C.Name AS CustomerName,
        S.Name AS PartyName,
        OrderDate,
        M_Items.Name AS ItemName,
        M_Items.id as ItemID,
        sum(BaseUnitQuantity) as BaseUnitQuantity,
        M_Items.BaseUnitID_id BaseUnitID ,
        (case when {unit}=0 then M_Items.BaseUnitID_id else {unit} end) UnitID
    FROM T_Orders
    JOIN TC_OrderItems ON Order_id = T_Orders.id
    JOIN M_Parties C ON Customer_id = C.id
    JOIN M_Parties S ON supplier_id=S.id
    JOIN M_Items ON Item_id = M_Items.id
    
    WHERE IsDeleted = 0
        AND OrderDate BETWEEN '{FromDate}' AND '{ToDate}'  {PartyDetails} {SupplierDetails} 
    GROUP BY C.id,S.id, OrderDate, M_Items.id , M_Items.BaseUnitID_id
) A
LEFT JOIN (
    SELECT
        C.id CustomerID,S.id PartyID,
        C.Name AS CustomerName,
        S.Name AS PartyName,
        InvoiceDate,
        M_Items.id as ItemID,
        M_Items.Name AS ItemName,
        sum(BaseUnitQuantity) as BaseUnitQuantity,
       
        M_Items.BaseUnitID_id BaseUnitID,
        (case when {unit}=0 then M_Items.BaseUnitID_id else {unit} end) UnitID
         
    FROM T_Invoices
    JOIN TC_InvoiceItems ON Invoice_id = T_Invoices.id
    JOIN M_Parties C ON Customer_id = C.id
    JOIN M_Parties S ON Party_id=S.id
    JOIN M_Items ON Item_id = M_Items.id
    
    WHERE InvoiceDate BETWEEN '{FromDate}' AND '{ToDate}'  {PartyDetails} {CustomerDetails} 
    GROUP BY C.id,S.id, InvoiceDate, M_Items.id, M_Items.BaseUnitID_id
) B
ON A.PartyName = B.PartyName
   AND A.OrderDate = B.InvoiceDate
   AND A.ItemName = B.ItemName
join M_Units ON M_Units.id=A.UnitID   
WHERE A.BaseUnitQuantity != COALESCE(B.BaseUnitQuantity, 0)
ORDER BY  A.PartyName, A.OrderDate''')

                # print(DemandVsReportquery.query)  
                if DemandVsReportquery:  
                    # print("SHRUR")              
                    for row in DemandVsReportquery:                       
                        DemandVsSupplyData.append({
                            "id":row.id,
                            "CustomerName" : row.CustomerName, 
                            "PartyName" :  row.PartyName,
                            "OrderDate":row.OrderDate,
                            "ItemName":row.ItemName,
                            "Demand":round(float(row.Demand),3),
                            "Supply":round(float(row.Supply),3),
                            "Difference" : round(float(row.Demand) - float(row.Supply) ,3  )  ,  
                            "UnitName" : row.UnitName                 
                        })                          
                # print(DemandVsSupplyData)
                log_entry = create_transaction_logNew(request, Data, 0, '', 432, 0, FromDate, ToDate, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DemandVsSupplyData})  
            log_entry = create_transaction_logNew(request, Data, 0, "Data Not Available", 431, 0, FromDate, ToDate, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not Available', 'Data': []}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, 'DemandVsReportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
     

class PendingGRNInvoicesAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                employee = request.user.Employee_id  
                
                PartyIDs = MC_ManagementParties.objects.filter(Employee=employee).values_list('Party_id', flat=True)

                PendingGRNQuery = T_Invoices.objects.raw('''SELECT 1 AS id, cust.Name AS CustomerName,COUNT(T_Invoices.id) AS PendingGRNCount
                                                            FROM T_Invoices
                                                            JOIN M_Parties cust ON cust.id = T_Invoices.Customer_id
                                                            JOIN  M_PartyType pt ON cust.PartyType_id = pt.id
                                                            LEFT JOIN  TC_GRNReferences ON T_Invoices.id = TC_GRNReferences.Invoice_id
                                                            WHERE TC_GRNReferences.Invoice_id IS NULL AND pt.IsRetailer = 0 AND  T_Invoices.Hide = 0
                                                            AND cust.id IN (%s)  
                                                            GROUP BY cust.Name''' % ','.join(map(str, PartyIDs)))

                response_data = [
                    {
                        "CustomerName": result.CustomerName,
                        "PendingGRNCount": result.PendingGRNCount
                    }
                    for result in PendingGRNQuery
                ]

                if response_data:
                    log_entry = create_transaction_logNew(request, response_data, 0, '', 434, 0)
                    return JsonResponse({'StatusCode': 200,'Status': True,'Message': 'Pending GRN invoices retrieved successfully.','Data': response_data})
                else:
                    log_entry = create_transaction_logNew(request, response_data, 0, "No pending GRNs Available", 434, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'No pending GRN invoices found.','Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'PendingGRNsReport:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400,'Status': False,'Message': str(e),  'Data': [] })



class GRNDiscrepancyReportAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data.get('Party', 0)
                GRNDiscrepancyData = []

                GetParties = f"AND T_GRNs.Customer_id = {Party}" if Party != 0 else ""

                GRNDiscrepancyQuery = TC_GRNItems.objects.raw(f'''SELECT TC_GRNItems.id, T_GRNs.GRNDate, T_GRNs.Party_id, T_GRNs.Customer_id, 
                                                                  T_GRNs.FullGRNNumber, T_Invoices.FullInvoiceNumber, T_Invoices.InvoiceDate, M_Items.Name AS ItemName,  
                                                                  CASE WHEN T_Invoices.Hide = 0 THEN 'Save' ELSE 'Hide' END AS GRNSaveStatus,
                                                                  '' AS HideComment,party.Name AS PartyName, 
                                                                  customer.Name AS CustomerName, T_GRNs.Comment, TC_GRNItems.DiscrepancyComment, M_GeneralMaster.Name as DiscrepancyReason,
                                                                  TC_GRNItems.Amount, TC_GRNItems.Quantity, MC_ItemUnits.BaseUnitConversion
                                                                  FROM TC_GRNItems
                                                                  JOIN T_GRNs ON TC_GRNItems.GRN_id = T_GRNs.id
                                                                  JOIN M_Items ON TC_GRNItems.Item_id = M_Items.id
                                                                  JOIN M_Parties party ON T_GRNs.Party_id = party.id
                                                                  JOIN M_Parties customer ON T_GRNs.Customer_id = customer.id
                                                                  LEFT JOIN TC_GRNReferences ON TC_GRNReferences.GRN_id = T_GRNs.id  
                                                                  LEFT JOIN T_Invoices ON T_Invoices.id = TC_GRNReferences.Invoice_id  
                                                                  LEFT JOIN M_GeneralMaster ON TC_GRNItems.DiscrepancyReason = M_GeneralMaster.id 
                                                                  LEFT JOIN MC_ItemUnits ON TC_GRNItems.Item_id = MC_ItemUnits.Item_id 
                                                                  AND MC_ItemUnits.IsBase = TRUE 
                                                                  AND MC_ItemUnits.IsDeleted = 0
                                                                  WHERE T_GRNs.GRNDate BETWEEN '{FromDate}' AND '{ToDate}'
                                                                  AND TC_GRNItems.DiscrepancyComment IS NOT NULL
                                                                  {GetParties}''')
                
                PartyID = f"AND T_Invoices.Customer_id = {Party}" if Party != 0 else ""

                HiddenInvoicesQuery = T_Invoices.objects.raw(f'''SELECT T_Invoices.id, T_Invoices.HideComment as Comment, FullInvoiceNumber, InvoiceDate, Party_id,
                                                                Customer_id, party.Name AS PartyName, customer.Name AS CustomerName,
                                                                M_Items.Name AS ItemName, TC_InvoiceItems.Quantity,MC_ItemUnits.BaseUnitConversion,
                                                                TC_InvoiceItems.Amount,
                                                                CASE WHEN T_Invoices.Hide = 0 THEN 'Save' ELSE 'Hide' END AS GRNSaveStatus
                                                                FROM T_Invoices
                                                                JOIN M_Parties party ON T_Invoices.Party_id = party.id
                                                                JOIN M_Parties customer ON T_Invoices.Customer_id = customer.id
                                                                JOIN TC_InvoiceItems ON T_Invoices.id = TC_InvoiceItems.Invoice_id
                                                                JOIN M_Items ON TC_InvoiceItems.Item_id = M_Items.id
                                                                LEFT JOIN MC_ItemUnits ON M_Items.id = MC_ItemUnits.Item_id
                                                                AND MC_ItemUnits.IsBase = TRUE 
                                                                AND MC_ItemUnits.IsDeleted = 0
                                                                WHERE T_Invoices.Hide = 1 AND HideComment IS NOT NULL
                                                                AND T_Invoices.InvoiceDate BETWEEN '{FromDate}' AND '{ToDate}'
                                                                 {PartyID}''')
                
                for row in GRNDiscrepancyQuery:
                    GRNDiscrepancyData.append({
                        "id": row.id,
                        "PartyID": row.Party_id,
                        "Warehouse": row.PartyName,
                        "SAPInvoiceNumber": row.FullInvoiceNumber,
                        "InvoiceDate": row.InvoiceDate,
                        "GRNID": row.FullGRNNumber,
                        "GRNSaveStatus": "Save" if row.GRNSaveStatus == "Save" else "Hide", 
                        "GRNSaveDate": row.GRNDate,
                        "CustomerID": row.Customer_id,
                        "PartyName": row.CustomerName,
                        "SKUName": row.ItemName,
                        "QtyBilled": row.Quantity,
                        "QtyUOM": row.BaseUnitConversion,
                        "LineAmountwithGST": row.Amount,
                        "DiscrepancyComment": row.Comment,
                        "HideComment": None, 
                        "DiscrepancyReason": row.DiscrepancyReason,
                        "DiscrepancyItemComment": row.DiscrepancyComment,
                    })

                for invoice in HiddenInvoicesQuery:
                    GRNDiscrepancyData.append({
                        "id": invoice.id,
                        "PartyID": invoice.Party_id,
                        "Warehouse": invoice.PartyName,
                        "SAPInvoiceNumber": invoice.FullInvoiceNumber,
                        "InvoiceDate":invoice.InvoiceDate,
                        "GRNID": None,
                        "GRNSaveStatus": "Save" if invoice.GRNSaveStatus == "Save" else "Hide", 
                        "GRNSaveDate": None,
                        "CustomerID": invoice.Customer_id,
                        "PartyName": invoice.CustomerName,
                        "SKUName": invoice.ItemName,
                        "QtyBilled": invoice.Quantity,
                        "QtyUOM": invoice.BaseUnitConversion,
                        "LineAmountwithGST": invoice.Amount,
                        "DiscrepancyComment": None,
                        "HideComment": invoice.Comment,
                        "DiscrepancyReason": None,
                        "DiscrepancyItemComment": None,
                    })
                if GRNDiscrepancyData:
                    log_entry = create_transaction_logNew(request, Data, 0, "", 442, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": "GRN Discrepancy Report retrieved successfully.","Data": GRNDiscrepancyData,})

                log_entry = create_transaction_logNew(request, Data, 0, "No discrepancies found", 442, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 204, "Status": True,"Message": "No GRN discrepancies found.","Data": [], })

        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, "GRNDiscrepancyReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400,"Status": False,"Message": str(e), "Data": [],})
        

class CouponCodeRedemptionReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        CouponCodeData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = CouponCodeData['FromDate']
                ToDate = CouponCodeData['ToDate']
                Party = int(CouponCodeData.get('Party', 0))
                SchemeID = int(CouponCodeData.get('SchemeID', 0))
                CouponCodeRedemptionData = []
                # print('ss')
                conditions,ss,ss1 = '','',''

                if Party != 0:
                    conditions=f" And I.Party = {Party}"

                if SchemeID != 0:
                    ss=f" And M_Scheme.id = {SchemeID}"
                    ss1=f" and InS.scheme= {SchemeID}"
                
                
               
                CouponCodeRedemptionQuery = M_GiftVoucherCode.objects.raw(f''' with SweetPOSDiscount as (SELECT I.InvoiceDate,I.FullInvoiceNumber,I.Party,SUM(aa.DiscountAmount) AS TotalDiscountAmount
                                FROM SweetPOS.T_SPOSInvoices AS I
                                JOIN SweetPOS.TC_SPOSInvoiceItems AS aa ON I.id = aa.Invoice_id
                                join SweetPOS.TC_InvoicesSchemes InS on InS.Invoice_id=I.id
                                where I.InvoiceDate between '{FromDate}' AND '{ToDate}' {conditions} {ss1}
                                GROUP BY I.InvoiceDate,I.FullInvoiceNumber,I.Party)
                
                                select M_Scheme.id,M_Scheme.SchemeName,M_Scheme.FromPeriod,M_Scheme.ToPeriod ,M_Scheme.SchemeValue,M_Parties.Name PartyName,I.VoucherCode,I.InvoiceDate,
                                I.InvoiceAmount,I.InvoiceNumber,
                                IFNULL((case when M_SchemeType.BillEffect=0 then M_Scheme.SchemeValue else TotalDiscountAmount end),0) DiscountAmount
                                from M_GiftVoucherCode I 
                                join M_Scheme on M_Scheme.QRPrefix=LEFT(I.VoucherCode,3)
                                join M_SchemeType on  M_Scheme.SchemeTypeID_id=M_SchemeType.id
                                join M_Parties on M_Parties.id=I.Party
                                left join  SweetPOSDiscount 
                                    ON SweetPOSDiscount.InvoiceDate = I.InvoiceDate
                                    AND SweetPOSDiscount.FullInvoiceNumber = I.InvoiceNumber
                                    AND SweetPOSDiscount.Party = I.Party
                                where UsageType= 'online' and I.IsActive = 0  
                                and I.InvoiceDate between '{FromDate}' AND '{ToDate}' {conditions} {ss}
                                union 
                                select M_Scheme.id, M_Scheme.SchemeName,M_Scheme.FromPeriod,M_Scheme.ToPeriod ,M_Scheme.SchemeValue,M_Parties.Name PartyName,I.VoucherCode,I.InvoiceDate,
                                I.GrandTotal InvoiceAmount,I.FullInvoiceNumber ,
                                ifnull((case when M_SchemeType.BillEffect=0 then M_Scheme.SchemeValue else (TotalDiscountAmount) end),0) DiscountAmount
                                from SweetPOS.T_SPOSInvoices I
                                join SweetPOS.TC_InvoicesSchemes InS on InS.Invoice_id=I.id
                                join M_Parties on M_Parties.id=I.Party
                                join M_Scheme on M_Scheme.id=InS.scheme
                                join M_SchemeType on  M_Scheme.SchemeTypeID_id=M_SchemeType.id
                                left join  SweetPOSDiscount 
                                    ON SweetPOSDiscount.InvoiceDate = I.InvoiceDate
                                    AND SweetPOSDiscount.FullInvoiceNumber = I.FullInvoiceNumber
                                    AND SweetPOSDiscount.Party = I.Party
                                where UsageType= 'offline' 
                                and I.InvoiceDate between '{FromDate}' AND '{ToDate}' {conditions} {ss1} ''')
                
                # print(CouponCodeRedemptionQuery)
                
                i=1
                for CouponCode in CouponCodeRedemptionQuery:
                
                    # print(CouponCode.DiscountAmount,CouponCode.InvoiceNumber)
                    CouponCodeRedemptionData.append({
                        "id": i,
                        "VoucherTypeID": CouponCode.VoucherType_id,
                        "VoucherCode": CouponCode.VoucherCode,
                        "UpdatedOn": CouponCode.UpdatedOn,
                        "InvoiceDate":CouponCode.InvoiceDate,
                        "InvoiceNumber": CouponCode.InvoiceNumber,
                        "InvoiceAmount": CouponCode.InvoiceAmount,
                        "PartyID": CouponCode.Party,
                        "PartyName": CouponCode.PartyName,
                        "client": CouponCode.client,
                        "SchemeID": CouponCode.id,
                        "SchemeName" : CouponCode.SchemeName,
                        "SchemePeriod" : str(CouponCode.FromPeriod) + ' To ' + str(CouponCode.ToPeriod),
                        "DiscountAmount": round(CouponCode.DiscountAmount,0)
                    })
                    i=i+1
                if CouponCodeRedemptionData:
                    log_entry = create_transaction_logNew(request, CouponCodeData, 0, "", 443, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": "CouponCodeRedemptionReport","Data": CouponCodeRedemptionData,})

                log_entry = create_transaction_logNew(request, CouponCodeData, 0, "No CouponCodeRedemptionReport found", 443, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 204, "Status": True,"Message": "No CouponCodeRedemptionReport found.","Data": [], })

        except Exception as e:
            log_entry = create_transaction_logNew(request, CouponCodeData, 0, "CouponCodeRedemptionReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400,"Status": False,"Message": Exception(e),"Data": [],})

        
        
class MATAVoucherRedeemptionClaimView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        MATAData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = MATAData['FromDate']
                ToDate = MATAData['ToDate']
                Party = MATAData['Party']
                SchemeID=MATAData['SchemeID']
                Party_list = Party.split(",")
                Scheme_list = SchemeID.split(",")
                
                conditions,ss,ss1 = '','',''

                if Party_list and any(p.strip() != '0' for p in Party_list):
                    conditions = f" AND I.Party IN ({','.join(Party_list)})"
                if Scheme_list and any(s.strip() != '0' for s in Scheme_list):
                    ss = f" AND M_Scheme.id IN ({','.join(Scheme_list)})"
                    ss1 = f" AND InS.scheme IN ({','.join(Scheme_list)})"
                   
                
                
               
                CouponCodeRedemptionQuery = M_GiftVoucherCode.objects.raw(f'''select * from 
                                ( with SweetPOSDiscount as (SELECT InS.scheme, I.Party,SUM(aa.DiscountAmount) AS TotalDiscountAmount
                                FROM SweetPOS.T_SPOSInvoices AS I
                                JOIN SweetPOS.TC_SPOSInvoiceItems AS aa ON I.id = aa.Invoice_id
                                join SweetPOS.TC_InvoicesSchemes InS on InS.Invoice_id=I.id
                                where I.InvoiceDate between '{FromDate}' AND '{ToDate}' {conditions} {ss1}
                                GROUP BY InS.scheme,I.Party)
                                                                          
                                select M_Scheme.id,M_Scheme.SchemeName,M_Scheme.ShortName,M_Scheme.FromPeriod,M_Scheme.ToPeriod ,M_Parties.id PartyID ,M_Parties.Name PartyName,count(*)count,
                                IFNULL((case when M_SchemeType.BillEffect=0 then sum(M_Scheme.SchemeValue) else TotalDiscountAmount end ),0)DiscountAmount,M_Scheme.SchemeValue
                                from M_GiftVoucherCode I 
                                join M_Scheme on M_Scheme.QRPrefix=LEFT(I.VoucherCode,3)
                                join M_SchemeType on  M_Scheme.SchemeTypeID_id=M_SchemeType.id
                                join M_Parties on M_Parties.id=I.Party
                                left join SweetPOSDiscount
                                    ON SweetPOSDiscount.scheme = M_Scheme.id
                                    AND SweetPOSDiscount.Party = I.Party
                                where UsageType= 'online' and I.IsActive = 0  
                                and I.InvoiceDate between '{FromDate}' AND '{ToDate}' {conditions} {ss}
                                group by  M_Scheme.id ,M_Parties.id,M_Scheme.SchemeValue
                                union 
                                select M_Scheme.id,M_Scheme.SchemeName,M_Scheme.ShortName,M_Scheme.FromPeriod,M_Scheme.ToPeriod ,M_Parties.id PartyID ,M_Parties.Name PartyName,count(*)count,
                                IFNULL((case when M_SchemeType.BillEffect=0 then sum(M_Scheme.SchemeValue) else TotalDiscountAmount end),0) DiscountAmount,M_Scheme.SchemeValue
                               from SweetPOS.T_SPOSInvoices I
                                join SweetPOS.TC_InvoicesSchemes InS on InS.Invoice_id=I.id
                                join M_Parties on M_Parties.id=I.Party
                                join M_Scheme on M_Scheme.id=InS.scheme
                                join M_SchemeType on  M_Scheme.SchemeTypeID_id=M_SchemeType.id
                                left join SweetPOSDiscount
                                    ON SweetPOSDiscount.scheme = M_Scheme.id
                                    AND SweetPOSDiscount.Party = I.Party
                                where UsageType= 'offline' 
                                and I.InvoiceDate between '{FromDate}' AND '{ToDate}' {conditions} {ss1}
                                group by  M_Scheme.id ,M_Parties.id,M_Scheme.SchemeValue)a
                                 order by PartyID ''',)
                
                # print(CouponCodeRedemptionQuery)
                
                CodeRedemptionData = []
                i=1
                for CouponCode in CouponCodeRedemptionQuery:
                

                    CodeRedemptionData.append({
                        "id": i,
                        # "VoucherTypeID": CouponCode.VoucherType_id,
                        # "VoucherCode": CouponCode.VoucherCode,
                        # "UpdatedOn": CouponCode.UpdatedOn,
                        # "InvoiceDate":CouponCode.InvoiceDate,
                        # "InvoiceNumber": CouponCode.InvoiceNumber,
                        # "InvoiceAmount": CouponCode.InvoiceAmount,
                        "PartyID": CouponCode.PartyID,
                        "FranchiseName": CouponCode.PartyName,
                        "SchemeID": CouponCode.id,
                        "TotalClaimAmount": round(CouponCode.DiscountAmount,0),
                        "SchemeName": CouponCode.SchemeName,
                        "VoucherCodeCount" : CouponCode.count,
                        "ClaimPerVoucher" : CouponCode.SchemeValue,
                        "SchemeShortName" : CouponCode.ShortName,
                        "SchemePeriod" : str(CouponCode.FromPeriod) + ' To ' + str(CouponCode.ToPeriod),
                    })
                    i=i+1
                # --------- format output ---------------------
                # CodeRedemptionData = []                    
                # for row in rows:
                #     CodeRedemptionData.append({
                #         "id": row[0],
                #         "FranchiseName": row[1],
                #         "SchemeName": row[2],            
                #         "VoucherCodeCount": row[3],
                #         "ClaimPerVoucher": row[5],
                #         "TotalClaimAmount": row[4],
                #         "InvoiceAmount": row[6],
                #     })  
                if CodeRedemptionData:
                    log_entry = create_transaction_logNew(request, MATAData, 0, "", 448, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": "CodeRedemptionReport","Data": CodeRedemptionData,})

                log_entry = create_transaction_logNew(request, MATAData, 0, "No CodeRedemptionReport found", 448, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 204, "Status": True,"Message": "No CodeRedemptionReport found.","Data": [], })

        except Exception as e:
            log_entry = create_transaction_logNew(request, MATAData, 0, "CodeRedemptionReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400,"Status": False,"Message": str(e), "Data": [],})



class PeriodicGRNReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        PeriodicGRNData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = PeriodicGRNData['FromDate']
                ToDate = PeriodicGRNData['ToDate']
                PartyID = PeriodicGRNData['PartyID']
                SupplierID=PeriodicGRNData['SupplierID']
                ItemID=PeriodicGRNData['ItemID']
                GRNType=PeriodicGRNData['GRNTypeID'] 
                PeriodicGRNdataData = []                            

                SupplierCondition = f"AND T_GRNs.Customer_id = {PartyID}" if PartyID != 0 else ""
          
                SupplierCondition = f"AND T_GRNs.Customer_id = {PartyID}" if PartyID != 0 else ""
          
                if SupplierID !="":
                    Supplier= f"AND T_GRNs.Party_id={SupplierID}"
                else:
                    Supplier=""
                    
                if ItemID!="":
                    Item= f"AND TC_GRNItems.Item_id={ItemID}"
                else:
                    Item=""
                
                if GRNType!="":
                    
                    if GRNType==199: 
                        # For Regular GRN   
                        GRNTypeID=f"AND T_GRNs.IsGRNType=1"
                    elif GRNType==200:
                        # For IB GRN
                        GRNTypeID=f"AND T_GRNs.IsGRNType=0"
                    else:
                        # For VDC GRN   
                        # This is for future development; currently, the VDC type is 0 and needs to be changed to 2
                        GRNTypeID=f"AND T_GRNs.IsGRNType=2"    
                else:
                    GRNTypeID=""
                PeriodicGRNQuery = T_GRNs.objects.raw(f'''SELECT T_GRNs.id, T_GRNs.GRNDate, T_GRNs.FullGRNNumber as GRNNo,
                                                        T_Orders.FullOrderNumber AS PO, T_GRNs.Party_id as SupplierID, 
                                                        M_Parties.Name AS SupplierName, T_GRNs.InvoiceNumber as ChallanNo, 
                                                        M_Items.id AS ItemID, M_Items.Name AS ItemName, TC_GRNItems.Quantity,
                                                        TC_GRNItems.Rate, BasicAmount, GSTAmount, Amount, DiscountType, Discount, 
                                                        DiscountAmount, CGST, SGST, IGST, CGSTPercentage, SGSTPercentage, 
                                                        IGSTPercentage, GSTPercentage, TC_GRNItems.Unit_id AS UnitID, 
                                                        M_Units.Name AS UnitName
                                                        FROM T_GRNs
                                                        JOIN TC_GRNItems ON T_GRNs.id = TC_GRNItems.GRN_id
                                                        JOIN M_Items ON TC_GRNItems.Item_id = M_Items.id
                                                        LEFT JOIN MC_ItemUnits ON TC_GRNItems.Unit_id = MC_ItemUnits.id
                                                        LEFT JOIN M_Units ON MC_ItemUnits.UnitID_id = M_Units.id
                                                        JOIN TC_GRNReferences ON T_GRNs.id = TC_GRNReferences.GRN_id
                                                        LEFT JOIN T_Orders ON TC_GRNReferences.Order_id = T_Orders.id
                                                        LEFT JOIN M_Parties ON T_GRNs.Party_id = M_Parties.id
                                                        WHERE T_GRNs.GRNDate BETWEEN '{FromDate}' AND '{ToDate}' {SupplierCondition}  {Supplier} {Item} {GRNTypeID}''')
                for Periodic in PeriodicGRNQuery:
                    PeriodicGRNdataData.append({
                        "id": Periodic.id,
                        "GRNDate": Periodic.GRNDate,
                        "GRNNo": Periodic.GRNNo,
                        "PO": Periodic.PO,
                        "SupplierID": Periodic.SupplierID,
                        "Supplier": Periodic.SupplierName,
                        "ChallanNo": Periodic.ChallanNo,
                        "ItemID": Periodic.ItemID,
                        "ItemName": Periodic.ItemName,
                        "Quantity": Periodic.Quantity,
                        "Rate": Periodic.Rate,
                        "BasicAmount": Periodic.BasicAmount,
                        "GSTAmount": Periodic.GSTAmount,
                        "Amount": Periodic.Amount,
                        "DiscountType": Periodic.DiscountType,
                        "Discount": Periodic.Discount,
                        "DiscountAmount": Periodic.DiscountAmount,
                        "CGST": Periodic.CGST,
                        "SGST": Periodic.SGST,
                        "IGST": Periodic.IGST,
                        "CGSTPercentage": Periodic.CGSTPercentage,
                        "SGSTPercentage": Periodic.SGSTPercentage,
                        "IGSTPercentage": Periodic.IGSTPercentage,
                        "GSTPercentage": Periodic.GSTPercentage,
                        "UnitID": Periodic.UnitID,
                        "Unit": Periodic.UnitName
                    })

                if PeriodicGRNdataData:
                    log_entry = create_transaction_logNew(request, PeriodicGRNData, PartyID, "PeriodicGRNReport", 452, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": "PeriodicGRNReport", "Data": PeriodicGRNdataData})

                log_entry = create_transaction_logNew(request, PeriodicGRNData, PartyID, "No PeriodicGRNReport found", 452, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 204, "Status": True, "Message": "No PeriodicGRNReport found.", "Data": []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, PeriodicGRNData, PartyID, "PeriodicGRNReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400, "Status": False, "Message": str(e), "Data": []})
        
       
class ManagerSummaryReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data.get('Party', 0)
                OrderData = []
                InvoiceData = []
                
                order_condition = f"AND Supplier_id = {Party}" if Party != 0 else ""
                
                OrderDetailsQuery = T_Orders.objects.raw(f'''SELECT T_Orders.id, FullOrderNumber, AdvanceAmount, OrderAmount,CreatedOn
                                                            FROM T_Orders
                                                            WHERE AdvanceAmount > 0 AND CAST(T_Orders.CreatedOn AS DATE) BETWEEN '{FromDate}' AND '{ToDate}'
                                                            {order_condition}''')

                for order in OrderDetailsQuery:
                    OrderData.append({
                        "id": order.id,
                        "FullOrderNumber": order.FullOrderNumber,
                        "AdvanceAmount": float(order.AdvanceAmount),
                        "OrderAmount": float(order.OrderAmount),
                        "CreatedOn" : order.CreatedOn,
                        "OrderDate" : order.OrderDate
                    })

                invoice_condition = f"AND inv.Party = {Party}" if Party != 0 else ""
                
                InvoicesDetailsQuery = T_Invoices.objects.raw(f'''SELECT inv.id, inv.FullInvoiceNumber, inv.GrandTotal, inv.AdvanceAmount, ord.FullOrderNumber, ord.OrderDate
                                                                FROM SweetPOS.T_SPOSInvoices inv
                                                                JOIN SweetPOS.TC_SPOSInvoicesReferences ref ON inv.id = ref.Invoice_id
                                                                JOIN FoodERP.T_Orders ord ON ref.Order = ord.id
                                                                WHERE inv.InvoiceDate BETWEEN '{FromDate}' AND '{ToDate}' AND inv.IsDeleted=0
                                                                {invoice_condition}''')

                for invoice in InvoicesDetailsQuery:
                    FullInvoiceNumber = f"{invoice.FullInvoiceNumber} ({invoice.FullOrderNumber} {invoice.OrderDate.strftime('%Y-%m-%d')})"
                    InvoiceData.append({
                        "id": invoice.id,
                        "FullInvoiceNumber": FullInvoiceNumber,
                        "GrandTotal": float(invoice.GrandTotal-invoice.AdvanceAmount),
                        "AdvanceAmount": float(invoice.AdvanceAmount) if invoice.AdvanceAmount is not None else "0.00"
                    })

                if OrderData or InvoiceData:
                    log_entry = create_transaction_logNew(request, Data, Party, "ManagerSummaryReport", 461, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 200,"Status": True,"Message": "","Data": [{"OrderData": OrderData,"InvoiceData": InvoiceData}]})

                log_entry = create_transaction_logNew(request, Data, Party, "No ManagerSummaryReport found", 461, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 204,"Status": True,"Message": "No ManagerSummary data found.", "Data": []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, Party, "ManagerSummaryReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400,"Status": False,"Message": str(e),"Data": []})


class BillDeletedSummaryReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        BillData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = BillData['FromDate']
                ToDate = BillData['ToDate']
                Party = BillData['Party']
                CashierID =BillData['Cashier']
                BillDeletedSummaryData = [] 
                query = f'''SELECT SweetPOS.T_SPOSInvoices.id, InvoiceDate, FullInvoiceNumber, GrandTotal, 
                            FoodERP.M_Users.LoginName AS UserName,  FoodERP.M_Parties.Name AS PartyName
                            FROM SweetPOS.T_SPOSInvoices
                            LEFT JOIN FoodERP.M_Users ON T_SPOSInvoices.CreatedBy = M_Users.id
                            LEFT JOIN FoodERP.M_Parties ON T_SPOSInvoices.Party = M_Parties.id
                            WHERE IsDeleted = 1 AND InvoiceDate BETWEEN '{FromDate}' AND '{ToDate}' '''

                if Party > 0:
                    query += f' AND Party = {Party}'
                    
                if CashierID > "0" :   
                      query += f' AND M_Users.id in ({CashierID})'
                
                BillDeletedSummaryQuery = T_SPOSInvoices.objects.raw(query)  
        
                for bill in BillDeletedSummaryQuery:
                   
                    BillDeletedSummaryData.append({
                        "id": bill.id,
                        "InvoiceDate": bill.InvoiceDate,
                        "FullInvoiceNumber": bill.FullInvoiceNumber,
                        "GrandTotal": bill.GrandTotal,
                        "UserName":bill.UserName,
                        "PartyName": bill.PartyName                      
                    })
                if BillDeletedSummaryData:
                    log_entry = create_transaction_logNew(request, BillData, Party, "BillDeletedSummaryReport", 462, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": "BillDeletedSummaryReport","Data": BillDeletedSummaryData,})

                log_entry = create_transaction_logNew(request, BillData, Party, "No BillDeletedSummaryReport found", 462, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 204, "Status": True,"Message": "No BillDeletedSummaryReport found.","Data": [], })

        except Exception as e:
            log_entry = create_transaction_logNew(request, BillData, Party, "BillDeletedSummaryReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400,"Status": False,"Message": str(e), "Data": [],})

class ItemWiseConsumptionReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        itemData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = itemData['FromDate']
                ToDate = itemData['ToDate']
                Party = itemData['Party']
                ItemID =itemData['ItemID']                
                finish_products = []
                query = T_MaterialIssue.objects.raw(f'''SELECT 1 id,D.RawItemid, D.Item_id,
                    D.FinishItemName,D.RawItemName,
                    IFNULL(D.Quantity, 0) AS Quantity,
                    IFNULL(E.ProductionQuantity, 0) AS ProductionQuantity,
                    D.UnitName,UnitID_id
                    FROM (
                        SELECT 
                        FinishItem.id Item_id ,RawItem.id RawItemid,FinishItem.Name FinishItemName,RawItem.Name RawItemName,
                        M_Units.Name UnitName,MC_ItemUnits.UnitID_id ,SUM(TC_MaterialIssueItems.IssueQuantity) AS Quantity
                        FROM T_MaterialIssue  
                        JOIN TC_MaterialIssueItems ON TC_MaterialIssueItems.MaterialIssue_id = T_MaterialIssue.ID
                        JOIN M_Items FinishItem ON FinishItem.id=T_MaterialIssue.Item_id
                        JOIN M_Items RawItem ON RawItem.id=TC_MaterialIssueItems.Item_id
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=T_MaterialIssue.Unit_id
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
                        WHERE T_MaterialIssue.MaterialIssueDate BETWEEN '{FromDate}' AND '{ToDate}'  
                        AND TC_MaterialIssueItems.Item_id = {ItemID}  
                        AND T_MaterialIssue.Party_id = {Party}       
                        GROUP BY FinishItem.id
                        ) D
                    LEFT JOIN (
                        SELECT 
                            T_Production.Item_id AS ItemID2,
                            SUM(T_Production.ActualQuantity) AS ProductionQuantity 
                        FROM T_Production  
                        JOIN M_Items ON M_Items.ID = T_Production.Item_id 
                        WHERE T_Production.ProductionDate BETWEEN '{FromDate}' AND '{ToDate}' 
                        AND T_Production.Division_id = {Party}                       
                        GROUP BY T_Production.Item_id
                    ) AS E ON D.Item_id = E.ItemID2
                    WHERE IFNULL(D.Quantity, 0) != 0 OR IFNULL(E.ProductionQuantity, 0) != 0 ''')  
                

                raw_material_name = ""
                raw_material_id = 0
                raw_material_unit = ""
                query_list = list(query)
                if not query_list:
                    log_entry = create_transaction_logNew(request, itemData, Party, "No Data found", 480, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 204, "Status": True, "Message": "No Data found.", "Data": []})
                query2 = O_DateWiseLiveStock.objects.filter(
                        StockDate=FromDate, Party=Party, Item=ItemID).values('OpeningBalance', 'Unit_id')

                if query2:

                    unit_id = query[0].UnitID_id
                    OpeningBalance = UnitwiseQuantityConversion(
                        ItemID, query2[0]['OpeningBalance'], 0, query2[0]['Unit_id'], 0, unit_id, 0).ConvertintoSelectedUnit()
                else:

                    OpeningBalance = 0.00

                query3 = O_DateWiseLiveStock.objects.filter(
                    StockDate=ToDate, Party=Party, Item=ItemID).values('ClosingBalance', 'Unit_id')

                if query3:

                    ClosingBalance = UnitwiseQuantityConversion(
                        ItemID, query3[0]['ClosingBalance'], 0, query3[0]['Unit_id'], 0, unit_id, 0).ConvertintoSelectedUnit()

                else:
                    ClosingBalance = 0.00
                    
                RecieveQty = TC_GRNItems.objects.filter(
                    GRN__GRNDate__range=[FromDate, ToDate],
                    GRN__Customer_id=Party,
                    Item_id=ItemID
                ).aggregate(RecieveQuantity=Sum('Quantity'))
                RecieveQuantity=RecieveQty['RecieveQuantity'] or 0.00
                for row in query:
                    raw_material_name = row.RawItemName
                    raw_material_id = row.RawItemid
                    raw_material_unit = row.UnitName                    
                    finish_products.append({
                        "FinishItemID": row.Item_id,
                        "FinishProduct": row.FinishItemName,
                        "UsedQty": float(row.Quantity),
                        "ProductionQty": float(row.ProductionQuantity),
                    })
                
            response_data = {
            "RawMaterial": raw_material_name,
            "RawMaterialID": raw_material_id,
            "RawMaterialUnit": raw_material_unit,
             "OpeningBalance":OpeningBalance,
            "ClosingBalance":ClosingBalance,
            "RecieveQuantity":RecieveQuantity,
            "FinishproductDetails": finish_products 
            }
                
            log_entry = create_transaction_logNew(request, itemData, Party, "Success", 480, 0, FromDate, ToDate, 0)
            return JsonResponse({"StatusCode": 200, "Status": True,"Message": "Success.","Data": response_data, })

        except Exception as e:
            log_entry = create_transaction_logNew(request, itemData, Party, "ItemwiseConsumptionReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400,"Status": False,"Message": str(e), "Data": [],})
        
class BatchTraceabilityReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        WorkOrderData = JSONParser().parse(request)
        try:
            with transaction.atomic():
               
                WorkOrderID =WorkOrderData['WorkOrderID']                
                
                query1 = T_WorkOrder.objects.raw(f'''SELECT 1 id,(T_WorkOrder.WorkOrderNumber) BatchCardNo,T_WorkOrder.ID BacthCardID,T_WorkOrder.WorkOrderDate,
                M_Users.LoginName,Quantity,NumberOfLot,'Process Close' Status FROM T_WorkOrder 
                JOIN M_Users ON M_Users.ID=T_WorkOrder.CreatedBy 
                WHERE T_WorkOrder.ID={WorkOrderID}''')  
                query2 = T_WorkOrder.objects.raw(f'''SELECT 1 id,M_Items.ID ItemID,M_Items.Name ItemName,BOMQuantity,M_Units.Name UnitName FROM TC_WorkOrderItems 
                JOIN T_WorkOrder ON T_WorkOrder.ID=TC_WorkOrderItems.WorkOrder_id
                JOIN M_Items ON TC_WorkOrderItems.Item_id=M_Items.ID
                JOIN MC_ItemUnits ON MC_ItemUnits.ID=TC_WorkOrderItems.Unit_id
                JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
                WHERE T_WorkOrder.ID={WorkOrderID}''')
                
                query3 = T_MaterialIssue.objects.raw(f'''SELECT 1 id,M_Items.Name ItemName,TC_MaterialIssueItems.IssueQuantity Quantity,M_Units.Name UnitName,TC_MaterialIssueItems.Item_id,
                IFNULL((GRN_id),'') GRNNo,IFNULL((T_Production.ID),'') ProductionNo,
                IFNULL(T_Production.ID,'') ProductionID,IFNULL(TC_GRNItems.GRN_id,'') grnID,
                TC_MaterialIssueItems.BatchCode  FROM T_MaterialIssue 
                JOIN TC_MaterialIssueItems ON TC_MaterialIssueItems.MaterialIssue_id=T_MaterialIssue.ID 
                JOIN TC_MaterialIssueWorkOrders ON TC_MaterialIssueWorkOrders.MaterialIssue_id=T_MaterialIssue.ID
                JOIN M_Items ON M_Items.ID=TC_MaterialIssueItems.Item_id
                JOIN MC_ItemUnits ON MC_ItemUnits.ID=TC_MaterialIssueItems.Unit_id
                JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
                LEFT JOIN T_Production ON T_Production.BatchCode=TC_MaterialIssueItems.BatchCode and T_Production.Item_id=M_Items.ID
                LEFT JOIN TC_GRNItems ON TC_GRNItems.BatchCode=TC_MaterialIssueItems.BatchCode and TC_GRNItems.BatchCode!='0'
                WHERE TC_MaterialIssueItems.IssueQuantity > 0 AND TC_MaterialIssueWorkOrders.WorkOrder_id={WorkOrderID}''')
                
                query4 = T_Production.objects.raw(f'''SELECT  1 id ,(TC_MaterialIssueWorkOrders.WorkOrder_id) BatchCardNo,M_Items.ID ItemID,M_Items.Name ItemName,T_Production.NumberOfLot 
                ,ActualQuantity LotQty,T_Production.BatchCode,T_Production.ProductionDate,T_Production.PrintedBatchCode,T_Production.BestBefore
                FROM T_Production
                JOIN TC_ProductionMaterialIssue ON TC_ProductionMaterialIssue.Production_id=T_Production.ID
                JOIN T_MaterialIssue ON T_MaterialIssue.ID=TC_ProductionMaterialIssue.MaterialIssue_id
                JOIN TC_MaterialIssueWorkOrders ON TC_MaterialIssueWorkOrders.MaterialIssue_id=TC_ProductionMaterialIssue.MaterialIssue_id
                JOIN M_Items ON T_Production.Item_id=M_Items.ID
                WHERE TC_MaterialIssueWorkOrders.WorkOrder_id={WorkOrderID}''')
                
                query5=T_Production.objects.raw(f'''SELECT  1 id,T_Invoices.ID InvoiceID,T_Invoices.FullInvoiceNumber ,
                T_Invoices.InvoiceDate ,C.Name CustomerName,TC_InvoiceItems.Quantity ,
                TC_InvoiceItems.BatchCode from T_Production 
                JOIN TC_ProductionMaterialIssue ON TC_ProductionMaterialIssue.Production_id=T_Production.id
                JOIN O_BatchWiseLiveStock  ON O_BatchWiseLiveStock.Production_id=T_Production.id
                JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id
                JOIN TC_InvoiceItems ON TC_InvoiceItems.LiveBatch_id= O_LiveBatches.id
                JOIN T_Invoices ON T_Invoices.id=TC_InvoiceItems.Invoice_id
                JOIN M_Parties C ON C.id=T_Invoices.Customer_id
                JOIN TC_MaterialIssueWorkOrders ON TC_MaterialIssueWorkOrders.MaterialIssue_id=TC_ProductionMaterialIssue.MaterialIssue_id 
                WHERE WorkOrder_id={WorkOrderID}''')
                
                
                def to_dict_list(queryset, fields):
                    return [
                        {field: getattr(row, field) for field in fields}
                        for row in queryset
                    ]

                BatchDetails = to_dict_list(query1, ['BatchCardNo', 'BacthCardID', 'WorkOrderDate', 'LoginName', 'Quantity', 'NumberOfLot', 'Status'])
                BillOfMaterial = to_dict_list(query2, ['ItemID', 'ItemName', 'BOMQuantity', 'UnitName'])
                ActualMaterialIssue = to_dict_list(query3, ['ItemName', 'Quantity', 'UnitName', 'Item_id', 'GRNNo', 'ProductionNo', 'ProductionID', 'grnID', 'BatchCode'])
                ProductionDetails = to_dict_list(query4, ['BatchCardNo', 'ItemID', 'ItemName', 'NumberOfLot', 'LotQty', 'BatchCode', 'ProductionDate', 'PrintedBatchCode', 'BestBefore'])
                CustomerDispatchDetails=to_dict_list(query5,['InvoiceID','FullInvoiceNumber','InvoiceDate','CustomerName','Quantity','BatchCode'])
            
                
            log_entry = create_transaction_logNew(request, WorkOrderData, 0, "Success", 485, 0,0,0,0)
            return JsonResponse({"StatusCode": 200, "Status": True,"Message": "Success.","Data": {"WorkOrderDetails": BatchDetails,
                    "WorkOrderItems": BillOfMaterial,
                    "MaterialIssues": ActualMaterialIssue,
                    "ProductionDetails": ProductionDetails,
                    "CustomerDispatchDetails":CustomerDispatchDetails},})

        except Exception as e:
            log_entry = create_transaction_logNew(request, WorkOrderData, 0, "BatchTrasabilityReport: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400,"Status": False,"Message": str(e), "Data": [],})
        
class StockAdjustmentReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data['Party']
                StockAdjustmentData=list()
                WhereParty=""
                WherePartySweet=""
                if Party!="0":
                    WhereParty= f"AND T1.Party_id IN ({Party})"
                    WherePartySweet=f"AND T1.Party IN ({Party})"
                StockAdjustmnetquery =T_Stock.objects.raw(f'''SELECT 1 id, StockDate,ItemName,sum(Quantity) Quantity,Sum(Difference)Difference,Sum(BeforeAdjustment)BeforeAdjustment,PartyName,UnitName from (
                SELECT T1.StockDate, M_Items.Name AS ItemName,SUM(T1.Quantity)Quantity,Sum(T1.Difference)Difference,Sum(T1.Quantity - T1.Difference) AS BeforeAdjustment,M_Parties.Name PartyName,M_Units.Name UnitName
                FROM T_Stock T1 
                JOIN M_Items ON M_Items.ID = T1.Item_id
                JOIN M_Parties ON M_Parties.id=T1.Party_id
                JOIN MC_ItemUnits ON MC_ItemUnits.id=T1.Unit_id
                JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id   
                WHERE 
                    T1.StockDate BETWEEN '{FromDate}' AND '{ToDate}' {WhereParty} AND T1.IsStockAdjustment = 1  Group by T1.Item_id,StockDate,Party_id,StockDate,ItemName,PartyName
                UNION  
                SELECT  T1.StockDate, M_Items.Name AS ItemName,SUM(T1.Quantity)Quantity,Sum(T1.Difference)Difference,Sum(T1.Quantity - T1.Difference) AS BeforeAdjustment,M_Parties.Name PartyName,M_Units.Name UnitName
                FROM SweetPOS.T_SPOSStock T1 
                JOIN M_Items ON M_Items.ID = T1.Item
                JOIN M_Parties ON M_Parties.id=T1.Party
                JOIN MC_ItemUnits ON MC_ItemUnits.id=T1.Unit
                JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
                WHERE 
                    T1.StockDate BETWEEN  '{FromDate}' AND '{ToDate}' {WherePartySweet} AND T1.IsStockAdjustment = 1 Group by Item,StockDate,Party,StockDate,ItemName,PartyName )A
                Group By StockDate,ItemName,PartyName ORDER BY StockDate, ItemName,PartyName''')
                if StockAdjustmnetquery:                     
                    for row in StockAdjustmnetquery:                       
                        StockAdjustmentData.append({
                            # "id":row.id,
                            "StockDate":row.StockDate,
                            "ItemName":row.ItemName,
                            "Quantity":round(float(row.Quantity),3),
                            "Difference":round(float(row.Difference),3),
                            "BeforeAdjustment":round(float(row.BeforeAdjustment),3),
                            "PartyName":row.PartyName,
                            "UnitName":row.UnitName
                                                    
                        })    
                log_entry = create_transaction_logNew(request, Data, 0, '', 486, 0, FromDate, ToDate, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': StockAdjustmentData})  
            log_entry = create_transaction_logNew(request, Data, 0, "Data Not Available", 486, 0, FromDate, ToDate, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not Available', 'Data': []}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, 'StockAdjustmentReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

     