from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Views.V_CommFunction import GetOpeningBalance

from ..Serializer.S_Reports import PartyLedgerReportSerializer
from ..models import *


class PartyLedgerReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():

                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Party = Orderdata['Party']

                query=T_Invoices.objects.raw('''SELECT 
    1 id,
    InvoiceDate,
    BillNo,
    BankName,
    BranchName,
    ChequeDate,
    DocumentNo,
    ReceiptMode,
    InvoiceAmount,
    TotalTCS,
    ReceiptAmt,
    CashReceiptAmt,
    DebitNote,
    CreditNote,
    Flag,
    BasicAmount,
    BA5,
    BA12,
    BA18,
    GA5,
    GA12,
    GA18,
    Description
FROM
    ((SELECT 
        InvoiceDate,
            BillNo,
            BankName,
            BranchName,
            ChequeDate,
            DocumentNo,
            ReceiptMode,
            InvoiceAmount,
            TotalTCS,
            ReceiptAmt,
            CashReceiptAmt,
            DebitNote,
            CreditNote,
            Flag,
            BasicAmount,
            BA5,
            BA12,
            BA18,
            GA5,
            GA12,
            GA18,
            Description
            
    FROM
        (SELECT 
        InvoiceDate,
            T_Invoices.id,
            FullInvoiceNumber BillNo,
            "" AS BankName,
            "" AS BranchName,
            "" AS ChequeDate,
            "" AS DocumentNo,
            "" AS ReceiptMode,
            GrandTotal InvoiceAmount,
            TCSAmount TotalTCS,
            0 AS ReceiptAmt,
            0 AS CashReceiptAmt,
            1 AS Flag,
            0 AS DebitNote,
            0 AS CreditNote,
            "" AS Description
    FROM
        T_Invoices
    WHERE
        InvoiceDate BETWEEN %s AND %s
            AND Party_id = %s
            AND Customer_id = %s) a
    LEFT JOIN (SELECT 
        Invoice_id,
            SUM(BasicAmount) AS BasicAmount,
            
            SUM(CASE
                WHEN GSTPercentage = 5 THEN BasicAmount
                ELSE 0
            END) AS BA5,
            SUM(CASE
                WHEN GSTPercentage = 12 THEN BasicAmount
                ELSE 0
            END) AS BA12,
            SUM(CASE
                WHEN GSTPercentage = 18 THEN BasicAmount
                ELSE 0
            END) AS BA18,
            SUM(CASE
                WHEN GSTPercentage = 5 THEN GSTAmount
                ELSE 0
            END) AS GA5,
            SUM(CASE
                WHEN GSTPercentage = 12 THEN GSTAmount
                ELSE 0
            END) AS GA12,
            SUM(CASE
                WHEN GSTPercentage = 18 THEN GSTAmount
                ELSE 0
            END) AS GA18
    FROM
        TC_InvoiceItems
    GROUP BY Invoice_id) b ON a.id = b.Invoice_id) 
    
    UNION
    SELECT 
        ReceiptDate InvoiceDate,
            FullReceiptNumber BillNo,
            M_Bank.Name AS BankName,
            MC_PartyBanks.BranchName AS BranchName,
            ChequeDate ChequeDate,
            DocumentNo DocumentNo,
            M_GeneralMaster.Name AS ReceiptMode,
            0 AS InvoiceAmount,
            0 as TotalTCS,
            CASE
                WHEN ReceiptMode_id = 31 THEN 0
                ELSE AmountPaid
            END ReceiptAmt,
            CASE
                WHEN ReceiptMode_id = 31 THEN AmountPaid
                ELSE 0
            END CashReceiptAmt,
            2 AS Flag,
            0 AS DebitNote,
            0 AS CreditNote,
            0 AS BasicAmount,
            0 AS BA5,
            0 AS BA12,
            0 AS BA18,
            0 AS GA5,
            0 AS GA12,
            0 AS GA18,
            Description
    FROM
        T_Receipts
    LEFT JOIN MC_PartyBanks ON MC_PartyBanks.id = T_Receipts.Bank_id
    LEFT JOIN M_Bank ON M_Bank.id = MC_PartyBanks.Bank_id
    INNER JOIN M_GeneralMaster ON M_GeneralMaster.id = T_Receipts.ReceiptMode_id
    WHERE
        ReceiptDate BETWEEN %s AND %s
            AND T_Receipts.Party_id = %s
            AND T_Receipts.Customer_id = %s 
            
            UNION 
            SELECT 
        CRDRNoteDate InvoiceDate,
            FullNoteNumber BillNo,
            "" AS BankName,
            "" AS BranchName,
            "" AS ChequeDate,
            "" AS DocumentNo,
            "" AS ReceiptMode,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN T_CreditDebitNotes.GrandTotal
                ELSE 0
            END) AS InvoiceAmount,
            0 AS TotalTCS,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 0
                ELSE T_CreditDebitNotes.GrandTotal
            END) ReceiptAmt,
            0 AS CashReceiptAmt,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 3
                ELSE 4
            END) AS Flag,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN T_CreditDebitNotes.GrandTotal
                ELSE 0
            END) AS DebitNote,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 0
                ELSE T_CreditDebitNotes.GrandTotal
            END) CreditNote,
            0 AS BasicAmount,
            0 AS BA5,
            0 AS BA12,
            0 AS BA18,
            0 AS GA5,
            0 AS GA12,
            0 AS GA18,
            "" AS Description
    FROM
        T_CreditDebitNotes
    WHERE
        T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s
            AND Party_id = %s
            AND Customer_id = %s) q
ORDER BY InvoiceDate , Flag , BillNo ''',[FromDate,ToDate,Party,Customer,FromDate,ToDate,Party,Customer,FromDate,ToDate,Party,Customer])
               
                if not query:
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
                    Opening= GetOpeningBalance(Party,Customer,previous_date)
                    Closing= GetOpeningBalance(Party,Customer,ToDate)
                    temp=0
                    TaxFreeSale=0
                    TotalTaxableSale=0
                    TaxableSale5=0
                    TaxableSale12=0
                    TaxableSale18=0
                    GSTAmount5=0
                    GSTAmount12=0
                    GSTAmount18=0
                    TotalCreditNote=0
                    TotalDebitNote=0
                    TotalTCS=0
                    for a in PartyLedgerSerializedata:
                        if temp == 0:
                            temp = (float(Opening) + float(a['InvoiceAmount'])) - (float(a['ReceiptAmt'])+float(a['CashReceiptAmt']))
                        else:
                            temp = (temp + float(a['InvoiceAmount'])) - (float(a['ReceiptAmt'])+float(a['CashReceiptAmt']))
                        
                        TaxFreeSale=0.0
                        TotalTaxableSale = TotalTaxableSale + float(a["BasicAmount"])
                        TaxableSale5= TaxableSale5 + float(a["BA5"])
                        TaxableSale12= TaxableSale12 + float(a["BA12"])
                        TaxableSale18= TaxableSale18 + float(a["BA18"])
                        GSTAmount5= GSTAmount5 + float(a["GA5"])
                        GSTAmount12= GSTAmount12 + float(a["GA12"])
                        GSTAmount18= GSTAmount18 + float(a["GA18"])
                        TotalCreditNote = TotalCreditNote + float(a["CreditNote"])
                        TotalDebitNote = TotalDebitNote + float(a["DebitNote"])
                        TotalTCS = TotalTCS + float(a["TotalTCS"])
                        if a['BankName'] is None : 
                            BankName=''
                        else:
                            BankName=str(a['BankName'])
                        if a['BranchName'] is None : 
                            BranchName=''
                        else:
                            BranchName=str(a['BranchName'])
                        if a['DocumentNo'] is None : 
                            DocumentNo=''
                        else:
                            DocumentNo=str(a['DocumentNo'])
                        if a['ReceiptMode'] is None : 
                            ReceiptMode=''
                        else:
                            ReceiptMode= str(a['ReceiptMode'])  
                        if a['Description'] is None : 
                            Description=''
                        else:
                            Description= '('+ str(a['Description']) + ')' 
                        
                        print(BankName,'')
                        PartyLedgerItemDetails.append({
                            "Date": a['InvoiceDate'],
                            "DocumentNO": a['BillNo'],
                            "Particular": BankName+' '+BranchName+' '+DocumentNo+' '+ReceiptMode + ' ' + Description ,
                            "Amount": a['InvoiceAmount'],
                            "RecieptAmount": float(a['ReceiptAmt']) + float(a['CashReceiptAmt']),
                            "Cash": 0,
                            "Balance": float(temp),
                            
                        })
                    q1=M_Parties.objects.filter(id=Party).values("Name","PAN","GSTIN") 
                    q2=M_Parties.objects.filter(id=Customer).values("Name","PAN","GSTIN")    
                    PartyLedgerData.append({
                        "FormDate": FromDate,
                        "ToDate" : ToDate,
                        "Distributor": q1[0]['Name'],
                        "DistributorGSTIN" :q1[0]["GSTIN"],
                        "DistributorPAN" : q1[0]['PAN'],
                        "CustomerName": q2[0]['Name'],
                        "CustomerGSTIN" :  q2[0]["GSTIN"],
                        "CustomerPAN" : q2[0]["PAN"],
                        "Open": Opening,
                        "Close": Closing,
                        "TaxFreeSale" : TaxFreeSale,
                        "TotalTaxableSale": TotalTaxableSale,
                        "TaxableSale5": TaxableSale5,
                        "TaxableSale12" : TaxableSale12,
                        "TaxableSale18" : TaxableSale18,
                        "GSTAmount5" : GSTAmount5,
                        "GSTAmount12" : GSTAmount12,
                        "GSTAmount18" : GSTAmount18,
                        "TotalCreditNote" : TotalCreditNote,
                        "TotalDebitNote": TotalDebitNote,
                        "TotalTCS" : TotalTCS,
                        "InvoiceItems" : PartyLedgerItemDetails
                    })    
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyLedgerData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
