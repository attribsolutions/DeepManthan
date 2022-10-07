from genericpath import exists
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser,MultiPartParser, FormParser
from django.db.models import Q
from django.db.models import Max
from ..Serializer.S_Mrps import *
from ..Serializer.S_Margins import *
from ..models import *
from datetime import date


class MRPMaster:
    
    today = date.today() 
    def __init__(self,ItemID,DivisionID,PartyID,EffectiveDate):
        self.ItemID = ItemID
        self.DivisionID = DivisionID
        self.PartyID = PartyID
        self.EffectiveDate = EffectiveDate
    
    def GetTodaysDateMRP(self):
        if int(self.DivisionID)>0:
            D=Q(Division_id=self.DivisionID)
        else:
            D=Q(Division_id__isnull=True)
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        TodayDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(Item_id=self.ItemID,EffectiveDate__lte=self.today).order_by('-EffectiveDate','-id')[:1]
        # print(str(TodayDateItemMRPdata.query))
        if TodayDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(TodayDateItemMRPdata, many=True).data
            TodaysMRP=MRP_Serializer[0]['MRP']
        else:
            TodaysMRP= " "
            
        return TodaysMRP
     
    def GetEffectiveDateMRP(self):
        if int(self.DivisionID)>0:
            D=Q(Division_id=self.DivisionID)
        else:
            D=Q(Division_id__isnull=True)
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        EffectiveDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(Item_id=self.ItemID,EffectiveDate=self.EffectiveDate).order_by('-EffectiveDate','-id')[:1]
        # print(str(EffectiveDateItemMRPdata.query))
        # return str(EffectiveDateItemMRPdata.query)
        if EffectiveDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(EffectiveDateItemMRPdata, many=True).data
            EffectiveDateMRP =   MRP_Serializer[0]['MRP']
        else:
            EffectiveDateMRP = " "
        return EffectiveDateMRP
    
    def GetEffectiveDateMRPID(self):
        if int(self.DivisionID)>0:
            D=Q(Division_id=self.DivisionID)
        else:
            D=Q(Division_id__isnull=True)
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        EffectiveDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(Item_id=self.ItemID,EffectiveDate=self.EffectiveDate).order_by('-EffectiveDate','-id')[:1]
       
        if EffectiveDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(EffectiveDateItemMRPdata, many=True).data
            EffectiveDateID =   MRP_Serializer[0]['id']
        else:
            EffectiveDateID = " "
        return EffectiveDateID
    
    
    
###################################################################################################################

class MarginMaster:
    
    today = date.today() 
    def __init__(self,ItemID,PriceListID,PartyID,EffectiveDate):
        self.ItemID = ItemID
        self.PriceListID = PriceListID
        self.PartyID = PartyID
        self.EffectiveDate = EffectiveDate


    def GetTodaysDateMargin(self):
    
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=self.ItemID,PriceList_id=self.PriceListID,EffectiveDate__lte=self.today).order_by('-EffectiveDate','-id')[:1]
        # print(str(ItemMargindata.query))

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(ItemMargindata, many=True).data
            TodaysMargin =  Margin_Serializer[0]['Margin']
        else:
            TodaysMargin = " "

        return TodaysMargin
    
    def GetEffectiveDateMargin(self):
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=self.ItemID,PriceList_id=self.PriceListID,EffectiveDate=self.EffectiveDate).order_by('-EffectiveDate','-id')[:1]
        # print(str(ItemMargindata.query))

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(ItemMargindata, many=True).data
            EffectiveDateMargin=   Margin_Serializer[0]['Margin']
        else:
            EffectiveDateMargin = " "
                
        return EffectiveDateMargin

    def GetEffectiveDateMarginID(self):
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=self.ItemID,PriceList_id=self.PriceListID,EffectiveDate=self.EffectiveDate).order_by('-EffectiveDate','-id')[:1]
        # print(str(ItemMargindata.query))

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(ItemMargindata, many=True).data
            EffectiveDateMarginID=   Margin_Serializer[0]['id']
        else:
            EffectiveDateMarginID = " "
                
        return EffectiveDateMarginID
    

class MaxValueMaster:

    def __init__(self,TableName,ColumnName):
        self.TableName = TableName
        self.ColumnName = ColumnName
      
    
    def GetMaxValue(self):
        MaxCommonID=self.TableName.objects.aggregate(Max(self.ColumnName)) 
        a=MaxCommonID['CommonID__max'] 
        if a is None:
            a=1
        else:
            a=a+1
        return a    
            