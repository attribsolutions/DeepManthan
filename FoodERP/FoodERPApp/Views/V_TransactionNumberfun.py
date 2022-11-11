from ..models import *
from django.db.models import Max
from ..Serializer.S_Orders import *


class GetMaxNumber:

    def GetOrderNumber(*args):
        MaxOrderNumber=T_Orders.objects.filter(Division_id=args[0]).filter(OrderType=args[1]).order_by('-id')[:1]
        # return str(MaxOrderNumber.query)
        # MaxOrderNumber=T_Orders.objects.aggregate(Max('OrderNo')).filter(Division_id=args[0]).filter(OrderType=args[1]) 
        if MaxOrderNumber.exists():
            Order_serializer = T_OrderSerializerSecond(data=MaxOrderNumber,many=True)
            if Order_serializer.is_valid():
                return Order_serializer.data
        # if MaxOrderNumber.exists():
        #     Order_serializer = T_OrderSerializer(data=MaxOrderNumber)
        #     if Order_serializer.is_valid():
        #         return Order_serializer.data    
        # return str(MaxOrderNumber.query)
        
        # if a is None:
        #     a=1
        # else:
        #     a=a+1
        # no=MaxOrderNumber["OrderNo__max"]
        # return no
       
       
       
