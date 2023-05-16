from ..models import *
from ..Serializer.S_Orders import *
from datetime import date


class GetMaxNumber:

    def GetOrderNumber(*args):
        
        MaxOrderNumber=T_Orders.objects.filter(Division_id=args[0]).filter(OrderType=args[1]).values('OrderNo').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[2]
       
        if(not MaxOrderNumber):
          a = 1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:
                a=int(MaxOrderNumber[0]['OrderNo'])
                a=a+1
        return a
    
    def GetGrnNumber(*args):
        
        MaxGrnNumber=T_GRNs.objects.filter(Customer_id=args[0]).values('GRNNumber').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxGrnNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:    
                a=int(MaxGrnNumber[0]['GRNNumber'])
                a=a+1
        return a
    
    def GetChallanNumber(*args):
        
        MaxInvoiceNumber=T_Challan.objects.filter(Party_id=args[0]).values('ChallanNumber').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxInvoiceNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:    
                a=int(MaxInvoiceNumber[0]['ChallanNumber'])
                a=a+1
        return a
   
    
    def GetWorkOrderNumber(*args):
        
        MaxWorkOrderNumber=T_WorkOrder.objects.filter(Party_id=args[0]).values('WorkOrderNumber').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxWorkOrderNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:    
                a=int(MaxWorkOrderNumber[0]['WorkOrderNumber'])
                a=a+1
        return a
    
    def GetMaterialIssueNumber(*args):
        
        MaxMaterialIssueNumber=T_MaterialIssue.objects.filter(Party_id=args[0]).values('MaterialIssueNumber').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxMaterialIssueNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:    
                a=int(MaxMaterialIssueNumber[0]['MaterialIssueNumber'])
                a=a+1
        return a
    
    def GetDemandNumber(*args):
        
        MaxDemandNumber=T_Demands.objects.filter(Division_id=args[0]).filter(Customer_id=args[1]).values('DemandNo').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[2]
       
        if(not MaxDemandNumber):
          a = 1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:
                a=int(MaxDemandNumber[0]['DemandNo'])
                a=a+1
        return a
    
    def GetInvoiceNumber(*args):
        
        MaxInvoiceNumber=T_Invoices.objects.filter(Party_id=args[0]).values('InvoiceNumber').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxInvoiceNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:    
                a=int(MaxInvoiceNumber[0]['InvoiceNumber'])
                a=a+1
        return a

    def GetIBChallanNumber(*args):
        
        MaxIBChallanNumber=T_InterbranchChallan.objects.filter(Party_id=args[0]).values('IBChallanNumber').order_by('-id')[:1]
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxIBChallanNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else:    
                a=int(MaxIBChallanNumber[0]['IBChallanNumber'])
                a=a+1
        return a
        
    def GetIBInwardNumber(*args):
        
        MaxIBInwardNumber=T_InterBranchInward.objects.filter(Customer_id=args[0]).values('IBInwardNumber').order_by('-id')[:1]
        # print(str(MaxIBInwardNumber.query))
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxIBInwardNumber):
           
            a=1
        else:
            if(b==firstdatefinancial):
                
                a = 1
            else: 
                
                a=int(MaxIBInwardNumber[0]['IBInwardNumber'])
                a=a+1
        return a
    
    
    def GetLoadingSheetNumber(*args):
        
        MaxLoadingSheetNumber=T_LoadingSheet.objects.filter(Party_id=args[0]).values('No').order_by('-id')[:1]
        # print(str(MaxLoadingSheetNumber.query))
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxLoadingSheetNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else: 
                a=int(MaxLoadingSheetNumber[0]['No'])
                a=a+1
        return a
    
    
    def GetReceiptNumber(*args):
        
        MaxReceiptNumber=T_Receipts.objects.filter(Party_id=args[0]).values('ReceiptNo').order_by('-id')[:1]
        # print(str(MaxReceiptNumber.query))
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]
        if(not MaxReceiptNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else: 
                a=int(MaxReceiptNumber[0]['ReceiptNo'])
                a=a+1
        return a
    
    def GetCreditDebitNumber(*args):
        

        MaxCreditDebitNumber=T_CreditDebitNotes.objects.filter(Party_id=args[0], NoteType= args[1]).values('NoteNo').order_by('-id')[:1]
        # print(str(MaxReceiptNumber.query))
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[2]

        if(not MaxCreditDebitNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else: 
                a=int(MaxCreditDebitNumber[0]['NoteNo'])
                a=a+1
        return a
    
    def GetPurchaseReturnNumber(*args):
        
        MaxReturnNumber=T_PurchaseReturn.objects.filter(Party_id=args[0]).values('ReturnNo').order_by('-id')[:1]
        # print(str(MaxReceiptNumber.query))
        firstdatefinancial = date.today().strftime('%Y-04-01')
        b=args[1]

        if(not MaxReturnNumber):
            a=1
        else:
            if(b==firstdatefinancial):
                a = 1
            else: 
                a=int(MaxReturnNumber[0]['ReturnNo'])
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
       
        if (args[1]==37):
            Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Creditprefix')
        else:
            Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Debitprefix')
       
        if not Prifix :
            a=""
        else:
            if (args[1]==37):
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
    
class SystemBatchCodeGeneration:
    
    def GetGrnBatchCode(*args):
        today = date.today().strftime('%Y%m%d') 
         
        Date=str(today)   
        ItemID=str(args[0]) 
        CustomerID=str(args[1])
        IncrementedID=str(args[2])
        a=Date+"_"+ItemID+"_"+CustomerID+"_"+IncrementedID
        return a    
            
        
        
        
        
       
       
