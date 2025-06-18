from ..models import *
from ..Serializer.S_Orders import *

from django.db.models.functions import Coalesce
from datetime import datetime 

# import datetime
# import pdb

def GetYear(TDate):
    date = datetime.strptime(str(TDate), "%Y-%m-%d").date()
    #initialize the current year
    year_of_date=date.year     
    #initialize the current financial year start date
    financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()       
    if date<financial_year_start_date:           
        fs=  str(financial_year_start_date.year-1)+'-04-01'            
        fe=  str(financial_year_start_date.year)+'-03-31'           
    else:
        fs= str(financial_year_start_date.year)+ '-04-01'           
        fe= str(financial_year_start_date.year+1)+'-03-31'
    return fs,fe   
class GetMaxNumber:

    def GetOrderNumber(*args):  
       
        Return_year= GetYear(args[2])       
        fs,fe=Return_year
        MaxOrderNumber=T_Orders.objects.filter(Supplier_id=args[0]).filter(OrderType=args[1],OrderDate__range=(fs,fe)).values('OrderNo').order_by('-id')[:1]            
        # MaxOrderNumber=T_Orders.objects.raw('''SELECT 1 id , T_Orders.OrderNo FROM T_Orders WHERE (T_Orders.supplier_id = %s AND T_Orders.OrderType = %s  AND t_orders.OrderDate between %s and %s) ORDER BY T_Orders.id DESC LIMIT 1''',([args[0],args[1],fs,fe]))        
        if(not MaxOrderNumber):
                a=1
        else:               
            a=int(MaxOrderNumber[0]['OrderNo'])
            a=a+1
           
        return a
    def GetCSSPONumber(*args):   
        Return_year= GetYear(args[2])       
        fs,fe=Return_year
        MaxOrderNumber=T_Orders.objects.filter(Division_id=args[0]).filter(OrderType=args[1],OrderDate__range=(fs,fe)).values('OrderNo').order_by('-id')[:1]            
        # MaxOrderNumber=T_Orders.objects.raw('''SELECT 1 id , T_Orders.OrderNo FROM T_Orders WHERE (T_Orders.supplier_id = %s AND T_Orders.OrderType = %s  AND t_orders.OrderDate between %s and %s) ORDER BY T_Orders.id DESC LIMIT 1''',([args[0],args[1],fs,fe]))        
        if(not MaxOrderNumber):
                a=1
        else:               
            a=int(MaxOrderNumber[0]['OrderNo'])
            a=a+1
           
        return a
    
    def GetGrnNumber(*args):       
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year   
        MaxGrnNumber=T_GRNs.objects.filter(Customer_id=args[0],GRNDate__range=(fs,fe)).values('GRNNumber').order_by('-id')[:1]          
        # MaxGrnNumber=T_GRNs.objects.raw('''SELECT T_GRNs.GRNNumber FROM T_GRNs WHERE T_GRNs.Customer_id = %s and T_GRNs.GrnDate between %s and %s  ORDER BY T_GRNs.id DESC LIMIT 1''',([args[0],fs,fe]))
        if(not MaxGrnNumber):
            a=1
        else:               
            a=int(MaxGrnNumber[0]['GRNNumber'])
            a=a+1
        return a
    
    def GetChallanNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year 
        MaxChallanNumber=T_Challan.objects.filter(Party_id=args[0],ChallanDate__range=(fs,fe)).values('ChallanNumber').order_by('-id')[:1]
        if(not MaxChallanNumber):
                a=1
        else:               
            a=int(MaxChallanNumber[0]['ChallanNumber'])
            a=a+1 
        return a
    def GetVDCChallanNumber(*args):        
      
        Return_year= GetYear(args[1])       
        fs,fe=Return_year 
        MaxChallanNumber=T_Challan.objects.filter(Customer_id=args[0],ChallanDate__range=(fs,fe)).values('ChallanNumber').order_by('-id')[:1]
        
        if(not MaxChallanNumber):
                a=1
        else:               
            a=int(MaxChallanNumber[0]['ChallanNumber'])
            a=a+1 
        return a
   
   
    
    def GetWorkOrderNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year  
        MaxWorkOrderNumber=T_WorkOrder.objects.filter(Party_id=args[0],WorkOrderDate__range=(fs,fe)).values('WorkOrderNumber').order_by('-id')[:1]
        if(not MaxWorkOrderNumber):
                a=1
        else:               
            a=int(MaxWorkOrderNumber[0]['WorkOrderNumber'])
            a=a+1
        return a
    
    def GetMaterialIssueNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year  
        MaxMaterialIssueNumber=T_MaterialIssue.objects.filter(Party_id=args[0],MaterialIssueDate__range=(fs,fe)).values('MaterialIssueNumber').order_by('-id')[:1]
        if(not MaxMaterialIssueNumber):
                a=1
        else:               
            a=int(MaxMaterialIssueNumber[0]['MaterialIssueNumber'])
            a=a+1
        return a
    
    def GetDemandNumber(*args):        
        
        Return_year= GetYear(args[2])       
        fs,fe=Return_year  
        MaxDemandNumber=T_Demands.objects.filter(Division_id=args[0],).filter(Customer_id=args[1],DemandDate__range=(fs,fe)).values('DemandNo').order_by('-id')[:1]
        if(not MaxDemandNumber):
                a=1
        else:               
            a=int(MaxDemandNumber[0]['DemandNo'])
            a=a+1
        
        return a
    
    def GetInvoiceNumber(*args):            
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year    
        MaxInvoiceNumber=T_Invoices.objects.filter(Party_id=args[0],InvoiceDate__range=(fs,fe)).values('InvoiceNumber').order_by('-id')[:1] 
             
        max_number = T_DeletedInvoices.objects.filter(Party=args[0],InvoiceDate__range=(fs,fe)).aggregate(max_number=Max('InvoiceNumber'))['max_number']      
        
        
        if MaxInvoiceNumber or max_number:
            
            if(MaxInvoiceNumber):   
                max_invoice = int(MaxInvoiceNumber[0]['InvoiceNumber'])            
            else:
                max_invoice = 0

            if(max_number):    
                max_deleted = int(max_number)         
            else: 
                max_deleted =0

            if max_invoice > max_deleted:
                a = max_invoice + 1                
            else:
                a = max_deleted + 1
                
        else:  
             
            a = 1  

                    
        return a
    

    def GetIBChallanNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year 
        MaxIBChallanNumber=T_InterbranchChallan.objects.filter(Party_id=args[0],IBChallanDate__range=(fs,fe)).values('IBChallanNumber').order_by('-id')[:1]
        if(not MaxIBChallanNumber):
                a=1
        else:               
            a=int(MaxIBChallanNumber[0]['IBChallanNumber'])
            a=a+1
        return a
        
    def GetIBInwardNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year 
        MaxIBInwardNumber=T_InterBranchInward.objects.filter(Customer_id=args[0],IBInWardDate__range=(fs,fe)).values('IBInwardNumber').order_by('-id')[:1]
        if(not MaxIBInwardNumber):
                a=1
        else:               
            a=int(MaxIBInwardNumber[0]['IBInwardNumber'])
            a=a+1
        return a
    
    
    def GetLoadingSheetNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year 
        MaxLoadingSheetNumber=T_LoadingSheet.objects.filter(Party_id=args[0],Date__range=(fs,fe)).values('No').order_by('-id')[:1]
        if(not MaxLoadingSheetNumber):
                a=1
        else:               
            a=int(MaxLoadingSheetNumber[0]['No'])
            a=a+1
        return a
    
    
    def GetReceiptNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year 
        MaxReceiptNumber=T_Receipts.objects.filter(Party_id=args[0],ReceiptDate__range=(fs,fe)).values('ReceiptNo').order_by('-id')[:1]
        if(not MaxReceiptNumber):
                a=1
        else:               
            a=int(MaxReceiptNumber[0]['ReceiptNo'])
            a=a+1
        return a
    
    def GetCreditDebitNumber(*args):   
        Return_year= GetYear(args[2])       
        fs,fe=Return_year 
        MaxCreditDebitNumber=T_CreditDebitNotes.objects.filter(Party_id=args[0], NoteType= args[1],CRDRNoteDate__range=(fs,fe)).values('NoteNo').order_by('-id')[:1]
        if(not MaxCreditDebitNumber):
                a=1
        else:               
            a=int(MaxCreditDebitNumber[0]['NoteNo'])
            a=a+1
        return a
    
    def GetPurchaseReturnNumber(*args):        
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year 
        MaxReturnNumber=T_PurchaseReturn.objects.filter(Party_id=args[0],ReturnDate__range=(fs,fe)).values('ReturnNo').order_by('-id')[:1]
        if(not MaxReturnNumber):
            a=1
        else:               
            a=int(MaxReturnNumber[0]['ReturnNo'])
            a=a+1
         
        return a
    def GetProductionNumber(*args):       
        
        Return_year= GetYear(args[1])       
        fs,fe=Return_year   
        MaxProductionNumber=T_Production.objects.filter(Division_id=args[0],ProductionDate__range=(fs,fe)).values('ProductionNumber').order_by('-id')[:1]          
        
        if(not MaxProductionNumber):
            a=1
        else:               
            a=int(MaxProductionNumber[0]['ProductionNumber'])
            a=a+1
        return a
    
    

class GetPrifix:
                 
    def GetOrderPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Orderprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['Orderprefix']
        return a
    
    def GetGrnPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Grnprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['Grnprefix']
        return a
    
    def GetDemandPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Demandprefix')
        if not Prifix :
            a=''
        else:
            a=Prifix[0]['Demandprefix']
        return a
    
    def GetChallanPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Challanprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['Challanprefix']
        return a
    
    def GetWorkOrderPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('WorkOrderprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['WorkOrderprefix']
        return a
    
    def GetMaterialIssuePrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('MaterialIssueprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['MaterialIssueprefix']
        return a
    
    def GetInvoicePrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Invoiceprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['Invoiceprefix']
        return a

    def GetIBChallanPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('IBChallanprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['IBChallanprefix']
        return a 
       
    def GetIBInwardPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('IBInwardprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['IBInwardprefix']
        return a
    
    def GetReceiptPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Receiptprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['Receiptprefix']
        return a
    
    
    def GetCRDRPrifix(*args):
       
        if (args[1]==37 or args[1]==39 ):
            Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Creditprefix')
        else:
            Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Debitprefix')
       
        if not Prifix :
            a=""
        else:
            if (args[1]==37 or args[1]==39):
                a=Prifix[0]['Creditprefix']
            else:
                a=Prifix[0]['Debitprefix']               
        return a
    
    def GetPurchaseReturnPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('PurchaseReturnprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['PurchaseReturnprefix']
        return a
    
    def GetProductionPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Productionprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['Productionprefix']
        return a
    
class SystemBatchCodeGeneration:
    
    def GetGrnBatchCode(*args):
        today = date.today().strftime('%Y%m%d') 
         
        Date=str(today)   
        ItemID=str(args[0]) 
        CustomerID=str(args[1])
        IncrementedID=str(args[2])
        a=Date+"_"+ItemID+"_"+CustomerID+"_"+IncrementedID
        return a    
            
        
        
        
        
       
       
