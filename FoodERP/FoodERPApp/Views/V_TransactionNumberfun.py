from ..models import *
from django.db.models import Max
from ..Serializer.S_Orders import *
from datetime import date


class GetMaxNumber:

    def GetOrderNumber(*args):
        
        MaxOrderNumber=T_Orders.objects.filter(Division_id=args[0]).filter(OrderType=args[1]).values('OrderNo').order_by('-id')[:1]
        today = date.today().strftime('%Y-04-01')
        b=args[2]
        if(b >= today and not MaxOrderNumber):
            a=1
        else:
            a=int(MaxOrderNumber[0]['OrderNo'])
            a=a+1
        return a
    
    def GetGrnNumber(*args):
        
        MaxGrnNumber=T_GRNs.objects.filter(Customer_id=args[0]).values('GRNNumber').order_by('-id')[:1]
        today = date.today().strftime('%Y-04-01')
        b=args[1]
        if(b >= today and not MaxGrnNumber):
            a=1
        else:
            a=int(MaxGrnNumber[0]['GRNNumber'])
            a=a+1
        return a
    
    def GetDeliveryChallanNumber(*args):

        MaxChallanNumber=T_DeliveryChallans.objects.filter(Customer_id=args[0]).values('ChallanNumber').order_by('-id')[:1]
        today = date.today().strftime('%Y-04-01')
        b=args[1]
        if(b >= today and not MaxChallanNumber):
            a=1
        else:
            a=int(MaxChallanNumber[0]['ChallanNumber'])
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
    
    def GetDeliveryChallanPrifix(*args):
        Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Challanprefix')
        if not Prifix :
            a=""
        else:
            a=Prifix[0]['Challanprefix']
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
            
        
        
        
        
       
       
