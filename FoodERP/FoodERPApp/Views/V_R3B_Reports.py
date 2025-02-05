from decimal import Decimal
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_R3B_Reports import *
from ..models import  *
from django.http import HttpResponse


class GSTR3BDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
   
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
           
        
                query = T_Invoices.objects.raw('''
        SELECT 
            1 as id,                                  
            NatureOfSupplies,
            SUM(TotalTaxableValue) as TotalTaxableValue,
            SUM(IntegratedTax) as IntegratedTax,
            SUM(CentralTax) as CentralTax,
            SUM(State_UTTax) as State_UTTax,
            SUM(Cess) as Cess
        FROM (
            SELECT 
                '(a) Outward Taxable supplies (other than zero rated, nil rated and exempted)' as NatureOfSupplies,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage != 0 THEN TC_InvoiceItems.BasicAmount ELSE 0 END) as TotalTaxableValue,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage != 0 THEN TC_InvoiceItems.IGST ELSE 0 END) as IntegratedTax,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage != 0 THEN TC_InvoiceItems.CGST ELSE 0 END) as CentralTax,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage != 0 THEN TC_InvoiceItems.SGST ELSE 0 END) as State_UTTax,
                0 as Cess
            FROM T_Invoices 
            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
            WHERE T_Invoices.Party_id = %s AND T_Invoices.InvoiceDate BETWEEN %s AND %s
            GROUP BY NatureOfSupplies
            UNION                             
            SELECT 
                '(a) Outward Taxable supplies (other than zero rated, nil rated and exempted)' as NatureOfSupplies,
                SUM(CASE WHEN Y.GSTPercentage != 0 THEN Y.BasicAmount ELSE 0 END) as TotalTaxableValue,
                SUM(CASE WHEN Y.GSTPercentage != 0 THEN Y.IGST ELSE 0 END) as IntegratedTax,
                SUM(CASE WHEN Y.GSTPercentage != 0 THEN Y.CGST ELSE 0 END) as CentralTax,
                SUM(CASE WHEN Y.GSTPercentage != 0 THEN Y.SGST ELSE 0 END) as State_UTTax,
                0 as Cess
            FROM SweetPOS.T_SPOSInvoices X
            JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id
            WHERE X.Party = %s AND Y.InvoiceDate BETWEEN %s AND %s AND X.IsDeleted=0
            GROUP BY NatureOfSupplies
            UNION
            SELECT 
                '(b) Outward Taxable supplies (zero rated)' as NatureOfSupplies,
                0 as TotalTaxableValue,
                0 as IntegratedTax,
                0 as CentralTax,
                0 as State_UTTax,
                0 as Cess                                                                   
            UNION
            SELECT 
                '(c) Other Outward Taxable supplies (Nil rated, exempted)' as NatureOfSupplies,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage = 0 THEN TC_InvoiceItems.BasicAmount ELSE 0 END) as TotalTaxableValue,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage = 0 THEN TC_InvoiceItems.IGST ELSE 0 END) as IntegratedTax,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage = 0 THEN TC_InvoiceItems.CGST ELSE 0 END) as CentralTax,
                SUM(CASE WHEN TC_InvoiceItems.GSTPercentage = 0 THEN TC_InvoiceItems.SGST ELSE 0 END) as State_UTTax,
                0 as Cess
            FROM T_Invoices 
            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
            WHERE T_Invoices.Party_id = %s AND T_Invoices.InvoiceDate BETWEEN %s AND %s
            GROUP BY NatureOfSupplies
            UNION 
            SELECT 
                '(c) Other Outward Taxable supplies (Nil rated, exempted)' as NatureOfSupplies,
                SUM(CASE WHEN Y.GSTPercentage = 0 THEN Y.BasicAmount ELSE 0 END) as TotalTaxableValue,
                SUM(CASE WHEN Y.GSTPercentage = 0 THEN Y.IGST ELSE 0 END) as IntegratedTax,
                SUM(CASE WHEN Y.GSTPercentage = 0 THEN Y.CGST ELSE 0 END) as CentralTax,
                SUM(CASE WHEN Y.GSTPercentage = 0 THEN Y.SGST ELSE 0 END) as State_UTTax,
                0 as Cess
            FROM SweetPOS.T_SPOSInvoices X
            JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id
            WHERE X.Party = %s AND Y.InvoiceDate BETWEEN %s AND %s AND X.IsDeleted=0
            GROUP BY NatureOfSupplies
            UNION                                  
            SELECT 
                '(d) Inward supplies (liable to reverse charge)' as NatureOfSupplies,
                0 as TotalTaxableValue,
                0 as IntegratedTax,
                0 as CentralTax,
                0 as State_UTTax,
                0 as Cess
            UNION
            SELECT 
                '(e) Non-GST Outward supplies' as NatureOfSupplies,
                0 as TotalTaxableValue,
                0 as IntegratedTax,
                0 as CentralTax,
                0 as State_UTTax,
                0 as Cess
        ) A
        GROUP BY NatureOfSupplies''', (Party, FromDate, ToDate, Party, FromDate, ToDate, Party, FromDate, ToDate, Party, FromDate, ToDate))
                                                    
                DOSAISLTRC = DOSAISLTRCSerializer(query, many=True).data
                
                if not DOSAISLTRC:
                    DOSAISLTRC = [{
                                    'Nature Of Supplies': None,
                                    'Total Taxable Value': None,
                                    'Integrated Tax': None,
                                    'Central Tax': None,
                                    'State / UT Tax': None,
                                    'Cess': None
                                }]
       
        
                
################################## 4.EligibleITC #############################################################################

                EligibleITCquery = T_Invoices.objects.raw('''SELECT 1 as id, '(A) ITC Available (Whether in full or part)' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(1) Import of goods' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(2) Import of services' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(3) Inward supplies liable to reverse charge (other than 1 & 2 above)' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(4) Inward supplies from ISD' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(5) All other ITC' AS Details,IFNULL(SUM(Total.ITC_IntegratedTax), 0) AS IntegratedTax,
                                    IFNULL(SUM(Total.ITC_CentralTax), 0) AS CentralTax, IFNULL(SUM(Total.ITC_State_UTTax), 0) AS State_UTTax, 0 AS Cess
                                FROM (SELECT SUM(TC_InvoiceItems.IGST) AS ITC_IntegratedTax, SUM(TC_InvoiceItems.CGST) AS ITC_CentralTax, SUM(TC_InvoiceItems.SGST) AS ITC_State_UTTax
                                    FROM T_Invoices
                                    JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
                                    WHERE T_Invoices.Customer_id = %s AND T_Invoices.InvoiceDate BETWEEN %s AND %s) AS Total
                                UNION
                                SELECT 1 as id, '(B) ITC Reversed' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(1) As per Rule 42 & 43 of SGST/CGST rules' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(2) Others' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(C) Net ITC Available (A)-(B)' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(D) Ineligible ITC' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS Cess
                                UNION
                                SELECT 1 as id, '(1) As per section 17(5) of CGST/SGST Act' AS Details, 0 AS IntegratedTax, 0 AS CentralTax, 0 AS State_UTTax, 0 AS C''',([Party],[FromDate],[ToDate]))
                EligibleITC = EligibleITCSerializer(EligibleITCquery, many=True).data
                if not EligibleITC:
                    EligibleITC = [{
                                    'Details': None,
                                    'Integrated Tax': None,
                                    'Central Tax': None,
                                    'State / UT Tax': None,
                                    'Cess': None
                                }]    
     
        
        
#####################   3.2 Of the supplies shown in 3.1 (a), details of inter-state supplies made to unregistered persons, composition taxable person and UIN holders#################################################
        
                query3 = T_Invoices.objects.raw('''SELECT 1 as id , PlaceOfSupplyState_UT, sum(TaxableValue) TaxableValue, SUM(AmountOfIntegratedTax) AmountOfIntegratedTax
                                FROM (
                                    SELECT T_Invoices.id, concat(M_States.StateCode, '-', M_States.Name) as PlaceOfSupplyState_UT,
                                        SUM(TC_InvoiceItems.BasicAmount) as TaxableValue, SUM(TC_InvoiceItems.IGST) as AmountOfIntegratedTax
                                    FROM T_Invoices
                                    JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
                                    JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
                                    JOIN M_States ON M_Parties.State_id = M_States.id
                                    WHERE T_Invoices.Party_id = %s AND T_Invoices.InvoiceDate BETWEEN %s AND %s
                                    GROUP BY T_Invoices.id, M_States.StateCode, M_States.Name
                                    UNION
                                    SELECT X.id, concat(M_States.StateCode, '-', M_States.Name) as PlaceOfSupplyState_UT,
                                        SUM(Y.BasicAmount) as TaxableValue, SUM(Y.IGST) as AmountOfIntegratedTax
                                    FROM SweetPOS.T_SPOSInvoices X
                                    JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id
                                    JOIN M_Parties ON M_Parties.id = X.Customer
                                    JOIN M_States ON M_Parties.State_id = M_States.id
                                    WHERE X.Party = %s AND X.InvoiceDate BETWEEN %s AND %s AND X.IsDeleted=0
                                    GROUP BY X.id, M_States.StateCode, M_States.Name) A
                                    GROUP BY PlaceOfSupplyState_UT''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                Query3 = Query3Serializer(query3, many=True).data
                
                if not Query3:
                    Query3 = [{
                                    'Place Of Supply State / UT': None,
                                    'Taxable Value': None,
                                    'Amount Of Integrated Tax': None
                                }]
        
                response_data = {
                    "DOSAISLTRC":  DOSAISLTRC ,
                    "EligibleITC": EligibleITC ,
                    "DetailsOfInterStateSupplies":  Query3 
                  
                }
              
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_data})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': Exception(e), 'Data': []})

    


  