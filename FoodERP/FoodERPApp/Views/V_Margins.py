from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from django.db.models import Max

from ..Serializer.S_Margins import *

from ..Serializer.S_Items import *

from ..Serializer.S_Parties import *

from .V_CommFunction import *

from ..models import *


class M_MarginsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaxCommonID=M_MarginMaster.objects.aggregate(Max('CommonID')) 
                print(MaxCommonID)
                a=MaxCommonID['CommonID__max'] 
                if a is None:
                    a=1
                else:
                    a=a+1
                M_Marginsdata = JSONParser().parse(request)    
                additionaldata= list()
                for b in M_Marginsdata:
                    b.update({'CommonID': a})
                    additionaldata.append(b)     
                M_Margins_Serializer = M_MarginsSerializer(data=additionaldata,many=True)
            if M_Margins_Serializer.is_valid():
                M_Margins_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Margins Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Margins_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class GETMarginDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PriceListID = request.data['PriceList']
                PartyID = request.data['Party']
                EffectiveDate = request.data['EffectiveDate']
                query = M_Items.objects.all()
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = M_ItemsSerializer01(query, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        Item= a['id']
                        Margin = GetCurrentDateMargin(Item,PriceListID,PartyID,EffectiveDate)
                        ItemList.append({
                            "id": Item,
                            "Name": a['Name'],
                            "CurrentMargin": Margin,
                            "Margin":""
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
   