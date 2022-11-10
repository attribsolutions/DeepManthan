from ..models import *
from django.db.models import Max


class GetMaxNumber:

    def GetOrderNumber(self,*args):
    
        MaxOrderNumber=T_Orders.objects.filter(Division=args[0]).filter(OrderType=args[1]).aggregate(Max(self.OrderNo)) 
        a=MaxOrderNumber['OrderNo'] 
        if a is None:
            a=1
        else:
            a=a+1
        return a  
       
       
       
#        from .V_TransactionNumberfun import *



# DivisionID = Orderdata.data['Division']
# OrderTypeID= Orderdata.data['OrderType']
# a=GetMaxNumber.GetOrderNumber(DivisionID,OrderTypeID)