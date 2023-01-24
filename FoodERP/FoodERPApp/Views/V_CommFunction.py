from decimal import Decimal
from genericpath import exists
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser,MultiPartParser, FormParser
from django.db.models import Q
from django.db.models import Max
import math  



from ..Serializer.S_CommFunction import *
from ..Serializer.S_Mrps import *
from ..Serializer.S_Margins import *
from ..Serializer.S_GSTHSNCode import *
from ..Serializer.S_GSTHSNCode import *
from ..models import *
from datetime import date



'''Common Functions List
1) class MaxValueMaster -  GetMaxValue
2) class MRPMaster - GetTodaysDateMRP, GetEffectiveDateMRP, GetEffectiveDateMRPID
3) class MarginMaster - GetTodaysDateMargin, GetEffectiveDateMargin, GetEffectiveDateMarginID
4) class GSTHsnCodeMaster - GetTodaysGstHsnCode, GetEffectiveDateGSTHSNCode, GetEffectiveDateGSTHSNCodeID
5) class UnitwiseQuantityConversion - GetBaseUnitQuantity, ConvertintoSelectedUnit
6) class ShowBaseUnitQtyOnUnitDropDown - ShowDetails(baseunitname), TrimQty(Baseunitqty)
7) class UnitwiseQuantityConversion - GetBaseUnitQuantity,ConvertintoSelectedUnit
8) class ShowBaseUnitQtyOnUnitDropDown -ShowDetails

'''

def GetO_BatchWiseLiveStock(ItemID,PartyID):
   
    items = O_BatchWiseLiveStock.objects.filter(Item=ItemID,Party=PartyID)
    total_Stock = sum(items.values_list('BaseUnitQuantity', flat=True))
    
    return total_Stock

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
        
        TodayDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(Item_id=self.ItemID,EffectiveDate__lte=self.today,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        # print(str(TodayDateItemMRPdata.query))
        if TodayDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(TodayDateItemMRPdata, many=True).data
            Mrpid = MRP_Serializer[0]['id']
            MRPs=MRP_Serializer[0]['MRP']
            Date=MRP_Serializer[0]['EffectiveDate']
            MRPDetails=list()
            MRPDetails.append({
                "TodaysMRP":MRPs,
                "Date": Date,
                "Mrpid":Mrpid
            })
        else:
            MRPDetails=list()
            MRPDetails.append({
                "TodaysMRP":"",
                "Date": "",
                "Mrpid":""
            })
            
        return MRPDetails
     
    def GetEffectiveDateMRP(self):
        if int(self.DivisionID)>0:
            D=Q(Division_id=self.DivisionID)
        else:
            D=Q(Division_id__isnull=True)
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        EffectiveDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(Item_id=self.ItemID,EffectiveDate=self.EffectiveDate,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        # print(str(EffectiveDateItemMRPdata.query))
        # return str(EffectiveDateItemMRPdata.query)
        if EffectiveDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(EffectiveDateItemMRPdata, many=True).data
            EffectiveDateMRP =   MRP_Serializer[0]['MRP']
        else:
            EffectiveDateMRP = ""
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
        
        EffectiveDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(Item_id=self.ItemID,EffectiveDate=self.EffectiveDate,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
       
        if EffectiveDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(EffectiveDateItemMRPdata, many=True).data
            EffectiveDateID =   MRP_Serializer[0]['id']
        else:
            EffectiveDateID = ""
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
        
        ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=self.ItemID,PriceList_id=self.PriceListID,EffectiveDate__lte=self.today,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        # print(str(ItemMargindata.query))

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(ItemMargindata, many=True).data
            Margin =  Margin_Serializer[0]['Margin']
            Date =  Margin_Serializer[0]['EffectiveDate']
            MarginDetails=list()
            MarginDetails.append({
                "TodaysMargin":Margin,
                "Date": Date,
            })
            
        else:
            MarginDetails=list()
            MarginDetails.append({
                "TodaysMargin":"",
                "Date": "",
            })

        return MarginDetails
    
    def GetEffectiveDateMargin(self):
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=self.ItemID,PriceList_id=self.PriceListID,EffectiveDate=self.EffectiveDate,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        # print(str(ItemMargindata.query))

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(ItemMargindata, many=True).data
            EffectiveDateMargin=   Margin_Serializer[0]['Margin']
        else:
            EffectiveDateMargin = ""
                
        return EffectiveDateMargin

    def GetEffectiveDateMarginID(self):
        
        if int(self.PartyID)>0:
            P=Q(Party_id=self.PartyID)
        else:
            P=Q(Party_id__isnull=True)
        
        ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=self.ItemID,PriceList_id=self.PriceListID,EffectiveDate=self.EffectiveDate,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        # print(str(ItemMargindata.query))

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(ItemMargindata, many=True).data
            EffectiveDateMarginID=   Margin_Serializer[0]['id']
        else:
            EffectiveDateMarginID = ""
                
        return EffectiveDateMarginID
    

class GSTHsnCodeMaster:
    
    today = date.today() 
    def __init__(self,ItemID,EffectiveDate):
        self.ItemID = ItemID
        self.EffectiveDate = EffectiveDate

    def GetTodaysGstHsnCode(self):
        
        TodayDateGstHsncodedata = M_GSTHSNCode.objects.filter(Item_id=self.ItemID,EffectiveDate__lte=self.today,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        # print(str(TodayDateGstHsncodedata.query))
        if TodayDateGstHsncodedata.exists():
            GSTHsnCode_Serializer = M_GstHsnCodeSerializer(TodayDateGstHsncodedata, many=True).data
            Gstid = GSTHsnCode_Serializer[0]['id']
            Gst=GSTHsnCode_Serializer[0]['GSTPercentage']
            HSNCode=GSTHsnCode_Serializer[0]['HSNCode']
            Details=list()
            Details.append({
                "GST":Gst,
                "HSNCode": HSNCode,
                "Gstid": Gstid
            })
            
        else:
            Details=list()
            Details.append({
                "GST":"",
                "HSNCode": "",
                "Gstid": ""
            })
            
        return Details
        
    def GetEffectiveDateGstHsnCode(self):
        EffectiveDateGstHsnCodedata = M_GSTHSNCode.objects.filter(Item_id=self.ItemID,EffectiveDate=self.EffectiveDate,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        if EffectiveDateGstHsnCodedata.exists():
            GSTHsnCode_Serializer = M_GstHsnCodeSerializer(EffectiveDateGstHsnCodedata, many=True).data
            Gst=GSTHsnCode_Serializer[0]['GSTPercentage']
            HSNCode=GSTHsnCode_Serializer[0]['HSNCode']
            Details=list()
            Details.append({
                "GST":Gst,
                "HSNCode": HSNCode,
            })
           
        else:
            Details=list()
            Details.append({
                "GST":"",
                "HSNCode": "",
            })
        return Details   
       

    def GetEffectiveDateGstHsnID(self):
        
        EffectiveDateGstHsndata = M_GSTHSNCode.objects.filter(Item_id=self.ItemID,EffectiveDate=self.EffectiveDate,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]
        if EffectiveDateGstHsndata.exists():
            GstHsnCode_Serializer = M_GstHsnCodeSerializer(EffectiveDateGstHsndata, many=True).data
            EffectiveDateID =   GstHsnCode_Serializer[0]['id']
        else:
            EffectiveDateID = ""
        return EffectiveDateID   
    
    
class UnitwiseQuantityConversion:
    
    def __init__(self,ItemID,InputQuantity,MCItemUnit,MUnits,ConversionMCItemUnit,ConversionMUnits):
        self.ItemID = ItemID
        self.InputQuantity = InputQuantity
        self.MCItemUnit = MCItemUnit
        self.MUnits = MUnits
        self.ConversionMCItemUnit = ConversionMCItemUnit
        self.ConversionMUnits = ConversionMUnits
       
        
        if(MCItemUnit == 0 & MUnits==0 ):
            BaseUnitQuantityQuery=MC_ItemUnits.objects.all().filter(Item=ItemID,IsBase=1)
            BaseUnitQuantitySerializer=ItemUnitsSerializer(BaseUnitQuantityQuery, many=True).data
            self.BaseUnitQuantity=BaseUnitQuantitySerializer[0]['BaseUnitQuantity']
        else:
        
            if(MCItemUnit == 0): 
                a=Q(UnitID=MUnits)
            else:
                a=Q(id=MCItemUnit)   
            
            BaseUnitQuantityQuery=MC_ItemUnits.objects.all().filter(Item=ItemID).filter( a )
            BaseUnitQuantitySerializer=ItemUnitsSerializer(BaseUnitQuantityQuery, many=True).data
            self.BaseUnitQuantity=BaseUnitQuantitySerializer[0]['BaseUnitQuantity']
            
        if(ConversionMCItemUnit !=0) or (ConversionMUnits!=0):
            if(ConversionMCItemUnit == 0): 
                b=Q(UnitID=ConversionMUnits)
            else:
                b=Q(id=ConversionMCItemUnit)
            ConversionUnitBaseQuantityQuery=MC_ItemUnits.objects.filter(Item=ItemID).filter( b )
            print(str(ConversionUnitBaseQuantityQuery.query))
            ConversionUnitBaseQuantitySerializer=ItemUnitsSerializer(ConversionUnitBaseQuantityQuery, many=True).data
            self.ConversionUnitBaseQuantity=ConversionUnitBaseQuantitySerializer[0]['BaseUnitQuantity']
          
    def GetBaseUnitQuantity(self):
        
        BaseUnitQuantity=float(self.InputQuantity) * float(self.BaseUnitQuantity)
       
        return BaseUnitQuantity   

    def ConvertintoSelectedUnit(self):
        BaseUnitQuantity=float(self.InputQuantity) * float(self.BaseUnitQuantity)
        ConvertedQuantity=   float(BaseUnitQuantity) /  float(self.ConversionUnitBaseQuantity)
        return ConvertedQuantity


class  ShowBaseUnitQtyOnUnitDropDown:
    def __init__(self,ItemID,MC_ItemUnitID,MC_ItemUnitBaseUnitQty):
        self.ItemID = ItemID
        self.MC_ItemUnitID = MC_ItemUnitID
        self.MC_ItemUnitBaseUnitQty = MC_ItemUnitBaseUnitQty
        
        
    def ShowDetails(self):    
        Itemsquery = M_Items.objects.filter(id=self.ItemID)
        if Itemsquery.exists():
            Itemsdata = ItemSerializerSecond(Itemsquery, many=True).data
            for a in Itemsdata:
                BaseUnitName=a['BaseUnitID']['Name']
            
        ItemUnitquery = MC_ItemUnits.objects.filter(Item=self.ItemID, IsBase=1).values('id')
        qwer=ItemUnitquery[0]['id']
        
        a = (self.MC_ItemUnitBaseUnitQty)
        valueAfterPoint = a.split('.')[1]
        valueAfterPoint = int(valueAfterPoint)
       
        if valueAfterPoint == 0:
            num_value1 = int(float(a))  
        else:
            num_value1 = Decimal(self.MC_ItemUnitBaseUnitQty).normalize()
        BaseUnitQuantity = num_value1
        
        if qwer == self.MC_ItemUnitID :
            baseunitconcat=""
        else:
            baseunitconcat=" ("+ str(BaseUnitQuantity)+" "+BaseUnitName+")"
        
        return  baseunitconcat
     
    
    