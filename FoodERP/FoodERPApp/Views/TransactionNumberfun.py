from ..models import *
from django.db.models import Max



def GetOrderNumber(self ):
   
    MaxCommonID=T_Orders.objects.filter(Division=1).filter(OrderType=1).aggregate(Max(self.OrderNo)) 
    # a=MaxCommonID['CommonID__max'] 
    #     if a is None:
    #         a=1
    #     else:
    #         a=a+1
    return MaxCommonID  