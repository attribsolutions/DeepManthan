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
from ..Serializer.S_GSTHSNCode import *
from ..models import *
from datetime import date



'''Common Functions List
1) class MaxValueMaster -  GetMaxValue from table Pass Parameter
2) class MRPMaster - TodaysDateMRP,EffectiveDateMRP,EffectiveDateMRPID
3) class MarginMaster - TodaysDateMargin,EffectiveDateMargin,EffectiveDateMarginID
4) class GSTHsnCodeMaster - TodaysDateGSTHSnCode ,EffectiveDateGSTHSNCode,EffectiveDateGSTHSNCodeID
'''


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