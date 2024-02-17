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
           
        
                query = T_Invoices.objects.raw('''SELECT 1 as id, '(a) Outward Taxable  supplies  (other than zero rated, nil rated and exempted)' NatureOfSupplies,sum(TC_InvoiceItems.BasicAmount) TotalTaxableValue,SUM(TC_InvoiceItems.IGST) IntegratedTax,sum(TC_InvoiceItems.CGST) CentralTax, SUM(TC_InvoiceItems.SGST)State_UTTax,'0'Cess
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            WHERE Party_id=%s AND  T_Invoices.InvoiceDate BETWEEN %s AND %s and  TC_InvoiceItems.GSTPercentage != 0
                                            UNION 
                                            SELECT 1 as id, '(b) Outward Taxable  supplies  (zero rated )' NatureOfSupplies, 0 TotalTaxableValue,0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id,'(c) Other Outward Taxable  supplies (Nil rated, exempted)' NatureOfSupplies,sum(TC_InvoiceItems.BasicAmount) TotalTaxableValue,SUM(TC_InvoiceItems.IGST) IntegratedTax,sum(TC_InvoiceItems.CGST) CentralTax, SUM(TC_InvoiceItems.SGST)State_UTTax,'0'Cess
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            WHERE  Party_id=%s AND T_Invoices.InvoiceDate BETWEEN  %s AND %s AND TC_InvoiceItems.GSTPercentage = 0
                                            UNION 
                                            SELECT 1 as id, '(d) Inward supplies (liable to reverse charge) ' NatureOfSupplies, 0 TotalTaxableValue,0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION 
                                            SELECT 1 as id, '(e) Non-GST Outward supplies' NatureOfSupplies, 0 TotalTaxableValue,0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                                                    
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

                EligibleITCquery = T_Invoices.objects.raw('''SELECT 1 as id, '(A) ITC Available (Whether in full or part)' Details,0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id,  '(1)   Import of goods ' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(2)   Import of services' Details,0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(3)   Inward supplies liable to reverse charge(other than 1 &2 above)' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(4)   Inward supplies from ISD' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(5)   All other ITC' Details,IFNULL(SUM(TC_InvoiceItems.IGST),0) IntegratedTax,IFNULL(sum(TC_InvoiceItems.CGST),0) CentralTax, IFNULL(SUM(TC_InvoiceItems.SGST),0) State_UTTax,'0'Cess
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            WHERE  T_Invoices.Customer_id=%s AND T_Invoices.InvoiceDate BETWEEN %s AND %s
                                            UNION
                                            SELECT 1 as id, ' (B) ITC Reversed' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(1)   As per Rule 42 & 43 of SGST/CGST rules ' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(2)   Others' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(C) Net ITC Available (A)-(B)' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, ' (D) Ineligible ITC' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(1)   As per section 17(5) of CGST//SGST Act' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess
                                            UNION
                                            SELECT 1 as id, '(2)   Others' Details, 0 IntegratedTax,0 CentralTax, 0 State_UTTax,0 Cess''',([Party],[FromDate],[ToDate]))
                EgibleITC = EligibleITCSerializer(EligibleITCquery, many=True).data
                
                if not EgibleITC:
                    EgibleITC = [{
                                    'Details': None,
                                    'Integrated Tax': None,
                                    'Central Tax': None,
                                    'State / UT Tax': None,
                                    'Cess': None
                                }]
     
        
        
#####################   3.2 Of the supplies shown in 3.1 (a), details of inter-state supplies made to unregistered persons, composition taxable person and UIN holders#################################################
        
                query3 = T_Invoices.objects.raw('''SELECT 1 as id, concat(M_States.StateCode,'-',M_States.Name) PlaceOfSupplyState_UT ,sum(TC_InvoiceItems.BasicAmount) TaxableValue,SUM(TC_InvoiceItems.IGST) AmountOfIntegratedTax
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            JOIN M_Parties ON M_Parties.id=T_Invoices.Customer_id
                                            JOIN M_States ON M_Parties.State_id=M_States.id
                                            WHERE  Party_id=%s AND T_Invoices.InvoiceDate BETWEEN %s AND %s   group by M_States.id''',([Party],[FromDate],[ToDate]))
                Query3 = Query3Serializer(query3, many=True).data
                
                if not Query3:
                    Query3 = [{
                                    'Place Of Supply State / UT': None,
                                    'Taxable Value': None,
                                    'Amount Of Integrated Tax': None
                                }]
        
                response_data = {
                    "DOSAISLTRC":  DOSAISLTRC ,
                    "EgibleITC": EgibleITC ,
                    "DetailsOfInterStateSupplies":  Query3 
                  
                }
              
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_data})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': Exception(e), 'Data': []})

    


  