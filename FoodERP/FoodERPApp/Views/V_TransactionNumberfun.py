from ..models import *
from django.db.models import Max
from ..Serializer.S_Orders import *


class GetMaxNumber:

    def GetOrderNumber(*args):
        
        MaxOrderNumber=T_Orders.objects.filter(Division_id=args[0]).filter(OrderType=args[1]).values('OrderNo').order_by('-id')[:1]
       
        if not MaxOrderNumber :
            a=1
        else:
            a=int(MaxOrderNumber[0]['OrderNo'])
            a=a+1
        
        return a
             
        
        
        
        
        
       
       
