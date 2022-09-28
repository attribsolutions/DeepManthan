from genericpath import exists
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser,MultiPartParser, FormParser
from django.db.models import Q

from ..Serializer.S_Mrps import *
from ..Serializer.S_Margins import *
from ..models import *



def GetCurrentDateMRP(ItemID,DivisionID,PartyID,EffectiveDate):
    if int(DivisionID)>0:
        D=Q(Division_id=DivisionID)
    else:
        D=Q(Division_id__isnull=True)
    
    if int(PartyID)>0:
        P=Q(Party_id=PartyID)
    else:
        P=Q(Party_id__isnull=True)
    
    ItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(Item_id=ItemID,EffectiveDate__lte=EffectiveDate).order_by('-EffectiveDate')
    
    # print(str(ItemMRPdata.query))
    # return str(ItemMRPdata.query)
    if ItemMRPdata.exists():
        MRP_Serializer = M_MRPsSerializer(ItemMRPdata, many=True).data
        return  MRP_Serializer[0]['MRP']
    else:
        return 0


def GetCurrentDateMargin(ItemID,PriceListID,PartyID,EffectiveDate):
   
    if int(PartyID)>0:
        P=Q(Party_id=PartyID)
    else:
        P=Q(Party_id__isnull=True)
    
    ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=ItemID,PriceList_id=PriceListID,EffectiveDate__lte=EffectiveDate).order_by('-EffectiveDate')
    
    # print(str(ItemMargindata.query))

    if ItemMargindata.exists():
        Margin_Serializer = M_MarginsSerializer(ItemMargindata, many=True).data
        return  Margin_Serializer[0]['Margin']
    else:
        return 0    