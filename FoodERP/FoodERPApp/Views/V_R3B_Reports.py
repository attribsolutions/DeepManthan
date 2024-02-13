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
        
                query = T_Invoices.objects.raw('''SELECT 1 as id, '(a) Outward Taxable  supplies  (other than zero rated, nil rated and exempted)' A,sum(TC_InvoiceItems.BasicAmount) Taxablevalue,SUM(TC_InvoiceItems.IGST) IGST,sum(TC_InvoiceItems.CGST) CGST, SUM(TC_InvoiceItems.SGST)SGST,'0'Cess
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            WHERE Party_id=%s AND  T_Invoices.InvoiceDate BETWEEN %s AND %s and  TC_InvoiceItems.GSTPercentage != 0
                                            UNION 
                                            SELECT 1 as id, '(b) Outward Taxable  supplies  (zero rated )' A, 0 Taxablevalue,0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id,'(c) Other Outward Taxable  supplies (Nil rated, exempted)' A,sum(TC_InvoiceItems.BasicAmount) Taxablevalue,SUM(TC_InvoiceItems.IGST) IGST,sum(TC_InvoiceItems.CGST) CGST, SUM(TC_InvoiceItems.SGST)SGST,'0'Cess
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            WHERE  Party_id=%s AND T_Invoices.InvoiceDate BETWEEN  %s AND %s AND TC_InvoiceItems.GSTPercentage = 0
                                            UNION 
                                            SELECT 1 as id, '(d) Inward supplies (liable to reverse charge) ' A, 0 Taxablevalue,0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION 
                                            SELECT 1 as id, '(e) Non-GST Outward supplies' A, 0 Taxablevalue,0 IGST,0 CGST, 0 SGST,0 Cess''',([Party],[FromDate],[ToDate],[Party],[FromDate],[ToDate]))
                                                    
                DOSAISLTRCdata = DOSAISLTRCSerializer(query, many=True).data
 
        
                
################################## 4.EligibleITC #############################################################################

                EligibleITCquery = T_Invoices.objects.raw('''SELECT 1 as id, '(A) ITC Available (Whether in full or part)' A,0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id,  '(1)   Import of goods ' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(2)   Import of services' A,0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(3)   Inward supplies liable to reverse charge(other than 1 &2 above)' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(4)   Inward supplies from ISD' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(5)   All other ITC' A,IFNULL(SUM(TC_InvoiceItems.IGST),0) IGST,IFNULL(sum(TC_InvoiceItems.CGST),0) CGST, IFNULL(SUM(TC_InvoiceItems.SGST),0) SGST,'0'Cess
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            WHERE  T_Invoices.Customer_id=%s AND T_Invoices.InvoiceDate BETWEEN %s AND %s
                                            UNION
                                            SELECT 1 as id, ' (B) ITC Reversed' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(1)   As per Rule 42 & 43 of SGST/CGST rules ' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(2)   Others' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(C) Net ITC Available (A)-(B)' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, ' (D) Ineligible ITC' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(1)   As per section 17(5) of CGST//SGST Act' A, 0 IGST,0 CGST, 0 SGST,0 Cess
                                            UNION
                                            SELECT 1 as id, '(2)   Others' A, 0 IGST,0 CGST, 0 SGST,0 Cess''',([Party],[FromDate],[ToDate]))
                EgibleITCdata = EligibleITCSerializer(EligibleITCquery, many=True).data
     
        
        
#####################   3.2 Of the supplies shown in 3.1 (a), details of inter-state supplies made to unregistered persons, composition taxable person and UIN holders#################################################
        
                query3 = T_Invoices.objects.raw('''SELECT 1 as id, concat(M_States.StateCode,'-',M_States.Name)states ,sum(TC_InvoiceItems.BasicAmount) Taxablevalue,SUM(TC_InvoiceItems.IGST) IGST
                                            FROM T_Invoices
                                            JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                                            JOIN M_Parties ON M_Parties.id=T_Invoices.Customer_id
                                            JOIN M_States ON M_Parties.State_id=M_States.id
                                            WHERE  Party_id=%s AND T_Invoices.InvoiceDate BETWEEN %s AND %s   group by M_States.id''',([Party],[FromDate],[ToDate]))
                Query3data = Query3Serializer(query3, many=True).data
        
                response_data = [
                    {"DOSAISLTRCdata":  DOSAISLTRCdata },
                    {"EgibleITCdata": EgibleITCdata },
                    {"DetailsOfInterStateSupplies":  Query3data }
                  
                ]
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_data})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

    


  