
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_R1_Reports import *
from ..models import  *
from django.http import HttpResponse

class GSTR1ExcelDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
                
                B2Bquery = T_Invoices.objects.raw('''SELECT T_Invoices.id, M_Parties.GSTIN AS GSTIN_UINOfRecipient,
                                                  M_Parties.Name AS ReceiverName, T_Invoices.FullInvoiceNumber AS InvoiceNumber,
                    T_Invoices.InvoiceDate AS InvoiceDate, (T_Invoices.GrandTotal + T_Invoices.TCSAmount) AS InvoiceValue,
                    concat(M_States.StateCode, '-', M_States.Name) AS PlaceOfSupply, 'N' AS ReverseCharge,
                    '' AS ApplicableOfTaxRate, 'Regular' AS InvoiceType, '' AS ECommerceGSTIN,
                    TC_InvoiceItems.GSTPercentage AS Rate, SUM(TC_InvoiceItems.BasicAmount) AS TaxableValue,
                    '0' AS CessAmount
                    FROM T_Invoices 
                    JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
                    JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
                    JOIN M_States ON M_States.id = M_Parties.State_id
                    WHERE Party_id = %s AND InvoiceDate BETWEEN %s AND %s AND M_Parties.GSTIN != ''
                    GROUP BY M_Parties.GSTIN, M_Parties.Name, T_Invoices.id, T_Invoices.InvoiceDate,
                    M_States.id, M_States.Name, TC_InvoiceItems.GSTPercentage''', (Party, FromDate, ToDate))
                
                B2B2 = B2BSerializer(B2Bquery, many=True).data
                
                
                B2Bquery1 = T_Invoices.objects.raw('''SELECT 1 as id, count(DISTINCT Customer_id) AS NoOfRecipients,
                    count(*) AS NoOfInvoices, sum(T_Invoices.GrandTotal+T_Invoices.TCSAmount) AS TotalInvoiceValue
                    FROM T_Invoices JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
                    WHERE T_Invoices.Party_id = %s AND InvoiceDate BETWEEN %s AND %s AND M_Parties.GSTIN !=''
                    ''', (Party, FromDate, ToDate))
                
                B2B1 = B2BSerializer2(B2Bquery1, many=True).data
                
                if not B2B1:
                    B2B1 = [{
                             'No Of Recipients': None,
                             'No Of Invoices': None, 
                             'Total Invoice Value': None
                             }]
                    
                if not B2B2:
                    B2B2 = [{
                             'GSTIN / UIN Of Recipient': None, 
                             'Receiver Name': None,
                             'Invoice Number': None, 
                             'Invoice Value': None, 
                             'Place Of Supply': None, 
                             'Reverse Charge': None, 
                             'Applicable Of TaxRate': None,
                             'Invoice Type':None, 
                             'ECommerceGSTIN': None,
                             'Rate': None, 
                             'Taxable Value': None,
                             'Cess Amount': None }]
                
                # Example data for the second sheet B2CL
                B2CLquery = T_Invoices.objects.raw('''SELECT T_Invoices.id, T_Invoices.FullInvoiceNumber AS InvoiceNumber, T_Invoices.InvoiceDate,
                    (T_Invoices.GrandTotal) AS InvoiceValue, CONCAT(M_States.StateCode, '-', M_States.Name) AS PlaceOfSupply,
                    '' AS ApplicableOfTaxRate, TC_InvoiceItems.GSTPercentage AS Rate,
                    SUM(TC_InvoiceItems.BasicAmount) AS TaxableValue, '0' AS CessAmount, '' AS ECommerceGSTIN
                    FROM T_Invoices 
                    JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                    JOIN M_Parties a ON a.id=T_Invoices.Party_id
                    JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                    JOIN M_States ON M_States.id=b.State_id
                    WHERE Party_id=%s AND InvoiceDate BETWEEN %s AND %s AND b.GSTIN != '' AND b.State_id != a.State_id
                    AND T_Invoices.GrandTotal > 250000
                    GROUP BY T_Invoices.id, T_Invoices.InvoiceDate, M_States.id, M_States.Name, TC_InvoiceItems.GSTPercentage''',
                    (Party, FromDate, ToDate))
                
                B2CL2 = B2CLSerializer(B2CLquery, many=True).data
             
                B2CLquery2 = T_Invoices.objects.raw('''SELECT 1 AS id, COUNT(*) AS NoOfInvoices, SUM(T_Invoices.GrandTotal) AS TotalInvoiceValue
                    FROM T_Invoices
                    JOIN M_Parties a ON a.id = T_Invoices.Party_id
                    JOIN M_Parties b ON b.id = T_Invoices.Customer_id
                    JOIN M_States ON M_States.id = b.State_id
                    WHERE Party_id = %s AND InvoiceDate BETWEEN %s AND %s AND b.GSTIN != '' AND b.State_id != a.State_id
                    AND T_Invoices.GrandTotal > 250000
                    GROUP BY T_Invoices.id''', (Party, FromDate, ToDate))
                
                B2CL1 = B2CLSerializer2(B2CLquery2, many=True).data
                
                # Check if B2CL is empty
                if not B2CL1:
                    B2CL1 = [{
                                'No. Of Invoices': None, 
                                'Total Invoice Value': None
                                }]
                    
                if not B2CL2:
                    B2CL2 = [{
                                'Invoice Number': None, 
                                'Invoice Date': None,
                                'Invoice Value': None, 
                                'Place Of Supply': None, 
                                'Applicable Of TaxRate': None,
                                'ECommerce GSTIN': None, 
                                'Rate': None,
                                'Taxable Value': None,
                                'Cess Amount': None
                                }]
                    
                # Example data for the third sheet B2CS  
                B2CSquery = T_Invoices.objects.raw('''SELECT 1 as id, 'OE' Type,concat(M_States.StateCode,'-',M_States.Name)PlaceOfSupply, 
                                                   '' ApplicableOfTaxRate ,TC_InvoiceItems.GSTPercentage Rate,
                                                   sum(TC_InvoiceItems.BasicAmount) TaxableValue ,'0' CessAmount,'' ECommerceGSTIN
                            from T_Invoices 
                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                            JOIN M_Parties a ON a.id=T_Invoices.Party_id
                            JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                            JOIN M_States ON M_States.id=b.State_id
                            where Party_id=%s and InvoiceDate BETWEEN %s AND %s and  b.GSTIN =''
                            and ((a.State_id = b.State_id) OR (a.State_id != b.State_id and T_Invoices.GrandTotal <= 250000))
                            group  by M_States.id,M_States.Name,TC_InvoiceItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
                                
                B2CS2 = B2CSSerializer(B2CSquery, many=True).data
                
                B2CSquery2 = T_Invoices.objects.raw('''SELECT 1 as id,sum(TC_InvoiceItems.BasicAmount) TotalTaxableValue ,'' TotalCess
                            from T_Invoices
                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                            JOIN M_Parties a ON a.id=T_Invoices.Party_id
                            JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                            JOIN M_States ON M_States.id=b.State_id
                            where Party_id=%s and InvoiceDate BETWEEN  %s AND %s and  b.GSTIN =''
                            and ((a.State_id = b.State_id) OR (a.State_id != b.State_id and T_Invoices.GrandTotal <= 250000))''',([Party],[FromDate],[ToDate]))
                                
                B2CS1 = B2CSSerializer2(B2CSquery2, many=True).data
                
                if not B2B1:
                    B2B1 = [{
                             'No. Of Invoices': None,
                             'Total Invoice Value': None
                             }]
                    
                if not B2CS2:
                    B2CS2 = [{
                             'Invoice Number': None, 
                             'Invoice Date': None,
                             'Invoice Value': None, 
                             'Place Of Supply': None, 
                             'Applicable Of TaxRate': None,
                             'ECommerceGSTIN': None,
                             'Rate': None, 
                             'Taxable Value': None,
                             'Cess Amount': None }]
                
                # Example data for the four sheet CDNR 
                CDNRquery = T_CreditDebitNotes.objects.raw('''SELECT T_CreditDebitNotes.id, M_Parties.GSTIN AS GSTIN_UINOfRecipient,M_Parties.Name AS ReceiverName,
                                                           T_CreditDebitNotes.FullNoteNumber AS NoteNumber,T_CreditDebitNotes.CRDRNoteDate AS NoteDate,M_GeneralMaster.Name NoteTypeName,
                                                           T_CreditDebitNotes.NoteType_id AS NoteValue,CONCAT(M_States.StateCode, '-', M_States.Name) PlaceOfSupply,
                                                           'N' ReverseCharge,'Regular' NoteSupplyType,(T_CreditDebitNotes.GrandTotal) GrandTotal,'' ApplicableOfTaxRate,
                                                           TC_CreditDebitNoteItems.GSTPercentage Rate,SUM(TC_CreditDebitNoteItems.BasicAmount) TaxableValue,'' CessAmount FROM T_CreditDebitNotes
                                JOIN TC_CreditDebitNoteItems ON TC_CreditDebitNoteItems.CRDRNote_id = T_CreditDebitNotes.id
                                JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id
                                JOIN M_States ON M_States.id = M_Parties.State_id
                                JOIN M_GeneralMaster ON  M_GeneralMaster.id = T_CreditDebitNotes.NoteType_id
                                WHERE T_CreditDebitNotes.Party_id = %s  AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND M_Parties.GSTIN != '' 
                                GROUP BY T_CreditDebitNotes.id, M_Parties.GSTIN , M_Parties.Name , T_CreditDebitNotes.FullNoteNumber , T_CreditDebitNotes.CRDRNoteDate,NoteTypeName, T_CreditDebitNotes.NoteType_id , M_States.id , M_States.Name , TC_CreditDebitNoteItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
                            
                CDNR2 = CDNRSerializer(CDNRquery, many=True).data
                
                CDNRquery2= T_CreditDebitNotes.objects.raw('''SELECT 1 as id, COUNT(DISTINCT A.Customer_id)NoOfRecipients,COUNT(A.CRDRNote_id) NoOfNotes,SUM(A.GrandTotal) TotalInvoiceValue,SUM(A.TaxbleAmount) TotalTaxableValue, 0 TotalCess
                        FROM (
                        SELECT  T_CreditDebitNotes.Customer_id,TC_CreditDebitNoteItems.CRDRNote_id,T_CreditDebitNotes.GrandTotal,SUM(TC_CreditDebitNoteItems.BasicAmount) TaxbleAmount
                        FROM TC_CreditDebitNoteItems
                        JOIN T_CreditDebitNotes ON T_CreditDebitNotes.id= TC_CreditDebitNoteItems.CRDRNote_id
                        JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id
                        WHERE Party_id=%s and T_CreditDebitNotes.CRDRNoteDate BETWEEN  %s  AND %s AND M_Parties.GSTIN != ''  Group by T_CreditDebitNotes.id)A''',([Party],[FromDate],[ToDate]))
                                
                CDNR1 = CDNRSerializer2(CDNRquery2, many=True).data
                
                if not CDNR1:
                    CDNR1 = [{
                             'No. Of Recipients': None,
                             'No. Of Notes': None,
                             'Total Invoice Value': None,
                             'Total Taxable Value': None,
                             'Total Cess': None
                             }]
                    
                if not CDNR2:
                    CDNR2 = [{
                             'GSTIN / UIN Of Recipient': None, 
                             'Receiver Name': None,
                             'Note Number': None, 
                             'Note Date': None, 
                             'Note Type Name': None, 
                             'Place Of Supply': None, 
                             'Reverse Charge': None,
                             'Note Value': None,
                             'Applicable Of TaxRate': None,
                             'Rate': None, 
                             'Taxable Value': None,
                             'Cess Amount': None }]
                
                # Example data for the five sheet CDNUR 
                CDNURquery = T_CreditDebitNotes.objects.raw('''SELECT T_CreditDebitNotes.id,'' URType, T_CreditDebitNotes.FullNoteNumber AS NoteNumber,T_CreditDebitNotes.CRDRNoteDate AS NoteDate, 
                                                            (CASE WHEN T_CreditDebitNotes.NoteType_id = 37 THEN 'C' ELSE 'D' END) NoteTypeID,
                                                            CONCAT(M_States.StateCode, '-', M_States.Name) PlaceOfSupply, (T_CreditDebitNotes.GrandTotal) NoteValue,
                                                            '' ApplicableOfTaxRate,TC_CreditDebitNoteItems.GSTPercentage Rate, SUM(TC_CreditDebitNoteItems.BasicAmount) TaxableValue, '' CessAmount
                        FROM T_CreditDebitNotes
                        JOIN TC_CreditDebitNoteItems ON TC_CreditDebitNoteItems.CRDRNote_id = T_CreditDebitNotes.id
                        JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id
                        JOIN M_States ON M_States.id = M_Parties.State_id
                        WHERE T_CreditDebitNotes.Party_id = %s AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND M_Parties.GSTIN = ''
                        GROUP BY  M_Parties.Name ,T_CreditDebitNotes.CRDRNoteDate,M_States.id ,M_States.Name ,TC_CreditDebitNoteItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
                        
                        # print(CDNURquery.query)
                CDNUR2 = CDNURSerializer(CDNURquery, many=True).data
                
                CDNURquery2= T_CreditDebitNotes.objects.raw('''SELECT 1 as id, COUNT(DISTINCT A.Customer_id)NoOfRecipients,COUNT(A.CRDRNote_id) NoOfNotes,SUM(A.GrandTotal) TotalNoteValue,SUM(A.TaxbleAmount)
                TotalTaxableValue, 0 TotalCess
                FROM (SELECT T_CreditDebitNotes.Customer_id, TC_CreditDebitNoteItems.CRDRNote_id,T_CreditDebitNotes.GrandTotal,
                SUM(TC_CreditDebitNoteItems.BasicAmount) TaxbleAmount 
                FROM TC_CreditDebitNoteItems 
                JOIN T_CreditDebitNotes ON T_CreditDebitNotes.id= TC_CreditDebitNoteItems.CRDRNote_id
                JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id 
                WHERE Party_id=%s and T_CreditDebitNotes.CRDRNoteDate BETWEEN
                %s AND  %s AND M_Parties.GSTIN = '' Group by T_CreditDebitNotes.id)A''',([Party],[FromDate],[ToDate]))
                    
                CDNUR1 = CDNURSerializer2(CDNURquery2, many=True).data
                
                if not CDNUR1:
                    CDNUR1 = [{
                             'No. Of Notes': None,
                             'Total Note Value': None,
                             'Total Taxable Value': None,
                             'Total Cess': None
                             }]
                    
                if not CDNUR2:
                    CDNUR2 = [{
                             'Receiver Name': None,
                             'Note Number': None, 
                             'Note Date': None, 
                             'Note Type Name': None, 
                             'Place Of Supply': None, 
                             'Reverse Charge': None,
                             'Note Value': None,
                             'Applicable Of TaxRate': None,
                             'Rate': None, 
                             'Taxable Value': None,
                             'Cess Amount': None }]
                
                # Example data for the six sheet CDNUR
                EXEMPquery = T_Invoices.objects.raw('''SELECT 1 as id , 'Inter-State supplies to registered persons' Description,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id  
                        WHERE Party_id= %s and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage= 0  and a.State_id != b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to registered persons' Description,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id= %s  and T_Invoices.InvoiceDate BETWEEN  %s AND %s  and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Inter-State supplies to unregistered persons' Description,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id= %s  and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id != b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to unregistered persons' Description,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id=%s  and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description
                        ''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                                # print(str(EXEMPquery.query))
                EXEMP2 = EXEMPSerializer(EXEMPquery, many=True).data
                     
                EXEMPquery2= T_Invoices.objects.raw(''' SELECT 1 as id, '' AA,sum(A.Total) TotalNilRatedSupplies,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                FROM (SELECT 1 as id , 'Inter-State supplies to registered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id  
                        WHERE Party_id= %s and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage= 0  and a.State_id != b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to registered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id= %s  and T_Invoices.InvoiceDate BETWEEN  %s AND %s  and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Inter-State supplies to unregistered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id= %s  and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id != b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to unregistered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id=%s  and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description)A
                        ''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                            
                EXEMP1 = EXEMP2Serializer2(EXEMPquery2, many=True).data
                
                   
                if not EXEMP1:
                    EXEMP1 = [{
                             'Total Nil Rated Supplies': None,
                             'Total Exempted Supplies': None,
                             'Total Non GST Supplies': None
                             }]
                    
                if not EXEMP2:
                    EXEMP2 = [{
                             'Description': None,
                             'Nil Rated Supplies': None,
                             'Exempted Other Than NilRated Non GST Supply': None,
                             'Non GST Supplies': None
                             }]
                
                # Example data for the seven sheet HSN 
                HSNquery = T_Invoices.objects.raw('''SELECT 1 as id, M_GSTHSNCode.HSNCode AS HSN,M_Items.Name Description, 'NOS-NUMBERS' AS UQC,sum(TC_InvoiceItems.QtyInNo) TotalQuantity,sum(TC_InvoiceItems.Amount)TotalValue,sum(TC_InvoiceItems.BasicAmount) TaxableValue, sum(TC_InvoiceItems.IGST)IntegratedTaxAmount,sum(TC_InvoiceItems.CGST)CentralTaxAmount,sum(TC_InvoiceItems.SGST)StateUTTaxAmount, '' CessAmount
                        FROM T_Invoices 
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                        JOIN M_Items ON M_Items.id=TC_InvoiceItems.Item_id
                        WHERE Party_id= %s  and T_Invoices.InvoiceDate BETWEEN %s AND %s  Group by id, M_GSTHSNCode.HSNCode,M_Items.Name''',([Party],[FromDate],[ToDate]))
                HSN2 = HSNSerializer(HSNquery, many=True).data
                
                HSNquery2= T_Invoices.objects.raw('''SELECT 1 as id, COUNT(DISTINCT(A.HSNCode))NoOfHSN,''a,''b,''c,sum(A.TotalValue) TotalValue,sum(A.TaxableValue) TotalTaxableValue,sum(A.IntegratedTaxAmount) TotalIntegratedTaxAmount,sum(A.CentralTaxAmount) TotalCentralTaxAmount,sum(A.StateUTTaxAmount) TotalStateUTTaxAmount, '' TotalCessAmount
                FROM (SELECT 1 as id, M_GSTHSNCode.HSNCode,M_Items.Name Description, 'NOS-NUMBERS' AS UQC,sum(TC_InvoiceItems.QtyInNo) TotalQuantity,sum(TC_InvoiceItems.Amount)TotalValue,sum(TC_InvoiceItems.BasicAmount) TaxableValue, sum(TC_InvoiceItems.IGST)IntegratedTaxAmount,sum(TC_InvoiceItems.CGST)CentralTaxAmount,sum(TC_InvoiceItems.SGST)StateUTTaxAmount, '' CessAmount
                        FROM T_Invoices 
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                        JOIN M_Items ON M_Items.id=TC_InvoiceItems.Item_id
                        WHERE Party_id=%s  and T_Invoices.InvoiceDate BETWEEN  %s AND  %s  Group by id, M_GSTHSNCode.HSNCode,M_Items.Name)A''',([Party],[FromDate],[ToDate]))
            
                HSN1 = HSN2Serializer2(HSNquery2, many=True).data
                
                if not HSN1:
                    HSN1 = [{
                             'No. Of HSN': None,
                             'Total Value': None,
                             'Total Invoice Value': None,
                             'Total Integrated Tax Amount': None,
                             'Total Central Tax Amount': None,
                             'Total State UT Tax Amount': None,
                             'Total Cess Amount': None,
                             }]
                    
                if not HSN2:
                    HSN2 = [{
                             'HSN': None, 
                             'Description': None,
                             'UQC': None, 
                             'Total Quantity': None, 
                             'Total Value': None, 
                             'Taxable Value': None, 
                             'Integrated Tax Amount': None,
                             'Central Tax Amount': None,
                             'State UT Tax Amount': None,
                             'Cess Amount': None }]
                
                # Example data for the eight sheet Docs  
                Docsquery = T_Invoices.objects.raw('''SELECT 1 as id, 'Invoices for outward supply' NatureOfDocument,MIN(T_Invoices.InvoiceNumber)Sr_No_From,max(T_Invoices.InvoiceNumber)Sr_No_To ,count(*)TotalNumber,(SELECT count(*)cnt from T_DeletedInvoices  where Party =%s and T_DeletedInvoices.InvoiceDate BETWEEN %s AND %s ) Cancelled ,'1' b
                                FROM T_Invoices  where Party_id =%s and T_Invoices.InvoiceDate BETWEEN %s AND %s
                                UNION
                                SELECT 1 as id, 'Credit Note' a,MIN(T_CreditDebitNotes.FullNoteNumber)MINID,MAX(T_CreditDebitNotes.FullNoteNumber)MAXID ,count(*)TotalNumber,'0' Cancelled ,'2' b
                                FROM T_CreditDebitNotes
                                WHERE  T_CreditDebitNotes.NoteType_id=37 and Party_id =%s and T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s
                                UNION
                                SELECT 1 as id, 'Debit Note' a, MIN(T_CreditDebitNotes.FullNoteNumber)MINID,MAX(T_CreditDebitNotes.FullNoteNumber)MAXID ,count(*)TotalNumber,'0' Cancelled,'3' b
                                FROM T_CreditDebitNotes  
                                WHERE  T_CreditDebitNotes.NoteType_id=38 AND Party_id =%s and T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s ''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                               
                Docs2 = DocsSerializer(Docsquery, many=True).data
            
                Docsquery2 = T_Invoices.objects.raw(''' SELECT 1 as id, '' AA,'' bb, '' cc,sum(A.cnt)TotalNumbers ,sum(A.TotalCancelled)TotalCancelled
                FROM (SELECT 1 as id, 'Invoices for outward supply' a,MIN(T_Invoices.InvoiceNumber)MINID,max(T_Invoices.InvoiceNumber)MAXID ,count(*)cnt,(SELECT count(*)cnt from T_DeletedInvoices  where Party =%s and T_DeletedInvoices.InvoiceDate BETWEEN %s AND %s ) TotalCancelled ,'1' b
                                FROM T_Invoices  where Party_id =%s and T_Invoices.InvoiceDate BETWEEN %s AND %s
                                UNION
                                SELECT 1 as id, 'Credit Note' a,MIN(T_CreditDebitNotes.FullNoteNumber)MINID,MAX(T_CreditDebitNotes.FullNoteNumber)MAXID ,count(*)TotalNumbers,'0' TotalCancelled ,'2' b
                                FROM T_CreditDebitNotes
                                WHERE  T_CreditDebitNotes.NoteType_id=37 and Party_id =%s and T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s
                                UNION
                                SELECT 1 as id, 'Debit Note' a, MIN(T_CreditDebitNotes.FullNoteNumber)MINID,MAX(T_CreditDebitNotes.FullNoteNumber)MAXID ,count(*)TotalNumbers,'0' TotalCancelled,'3' b
                                FROM T_CreditDebitNotes  
                                WHERE  T_CreditDebitNotes.NoteType_id=38 AND Party_id =%s and T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s )A ''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                           
                Docs1 = Docs2Serializer2(Docsquery2, many=True).data
                
                if not Docs1:
                    Docs1 = [{
                             'Total Numbers': None,
                             'Total Cancelled': None,
                             }]
                    
                if not Docs2:
                    Docs2 = [{
                             'Nature Of Document': None,
                             'Sr. No. From': None,
                             'Sr. No. To': None,
                             'Total Number': None,
                             'Cancelled': None
                             }]
                
                response_data = {
                    "B2B":  B2B1 + B2B2,
                    "B2CL": B2CL1 + B2CL2,
                    "B2CS":  B2CS1 + B2CS2,
                    "CDNR": CDNR1 + CDNR2,
                    "CDNUR":  CDNUR1 + CDNUR2,
                    "EXEMP": EXEMP1 + EXEMP2,
                    "HSN":  HSN1 + HSN2,
                    "Docs": Docs1 + Docs2 
                }
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_data})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': Exception(e), 'Data': []})
             
