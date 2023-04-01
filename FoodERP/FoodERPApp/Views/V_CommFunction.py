from django.db.models import Q
from django.db.models import Max



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
        if ItemMargindata.exists:
           
            P=Q(Party_id__isnull=True)
            ItemMargindata = M_MarginMaster.objects.filter(P).filter(Item_id=self.ItemID,PriceList_id=self.PriceListID,EffectiveDate__lte=self.today,IsDeleted=0).order_by('-EffectiveDate','-id')[:1]

        
        
       

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
        # if ItemMargindata.count() == 0:
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
    
    def __init__(self,ItemID,InputQuantity,MCItemUnit,MUnits,ConversionMCItemUnit,ConversionMUnits,ShowDeletedUnitAlso):
        self.ItemID = ItemID
        self.InputQuantity = InputQuantity
        self.MCItemUnit = MCItemUnit
        self.MUnits = MUnits
        self.ConversionMCItemUnit = ConversionMCItemUnit
        self.ConversionMUnits = ConversionMUnits
        self.ShowDeletedUnitAlso = ShowDeletedUnitAlso
       
        if(ShowDeletedUnitAlso == 1):
            aaa=Q()
        else:
            aaa=Q(IsDeleted=0) 
        if(MCItemUnit == 0 & MUnits==0 ):
            BaseUnitQuantityQuery=MC_ItemUnits.objects.all().filter(Item=ItemID,IsBase=1).filter( aaa )
            BaseUnitQuantitySerializer=ItemUnitsSerializer(BaseUnitQuantityQuery, many=True).data
            self.BaseUnitQuantity=BaseUnitQuantitySerializer[0]['BaseUnitQuantity']
        else:
        
            if(MCItemUnit == 0): 
                a=Q(UnitID=MUnits)
            else:
                a=Q(id=MCItemUnit)   
            
            BaseUnitQuantityQuery=MC_ItemUnits.objects.all().filter(Item=ItemID).filter( a ).filter( aaa )
     
            BaseUnitQuantitySerializer=ItemUnitsSerializer(BaseUnitQuantityQuery, many=True).data
         
            self.BaseUnitQuantity=BaseUnitQuantitySerializer[0]['BaseUnitQuantity']
            
        if(ConversionMCItemUnit !=0) or (ConversionMUnits!=0):
            if(ConversionMCItemUnit == 0): 
                b=Q(UnitID=ConversionMUnits)
            else:
                b=Q(id=ConversionMCItemUnit)
            ConversionUnitBaseQuantityQuery=MC_ItemUnits.objects.filter(Item=ItemID).filter( b ).filter( aaa )
            
            ConversionUnitBaseQuantitySerializer=ItemUnitsSerializer(ConversionUnitBaseQuantityQuery, many=True).data
            self.ConversionUnitBaseQuantity=ConversionUnitBaseQuantitySerializer[0]['BaseUnitQuantity']
          
    def GetBaseUnitQuantity(self):
        
        BaseUnitQuantity=float(self.InputQuantity) * float(self.BaseUnitQuantity)
       
        return BaseUnitQuantity   

    def ConvertintoSelectedUnit(self):
        BaseUnitQuantity=float(self.InputQuantity) * float(self.BaseUnitQuantity)
        ConvertedQuantity=   float(BaseUnitQuantity) /  float(self.ConversionUnitBaseQuantity)
        return ConvertedQuantity


    
class RateCalculationFunction:

    def __init__(self,BatchID,ItemID,PartyID,DivisionID,MUnit,MCItemUnit):
        self.ItemID     =   ItemID 
        self.PartyID    =   PartyID 
        self.BatchID    =   BatchID
        self.DivisionID =   DivisionID
        self.today      =   date.today()
       
        if(BatchID > 0):
            QueryForGSTAndMRP=O_LiveBatches.objects.filter(id=BatchID).values('MRP','GST')
            q1=M_MRPMaster.objects.filter(id=QueryForGSTAndMRP[0]['MRP']).values('MRP')
            if q1.exists:
                self.MRP = 0
            else:
                self.MRP = q1[0]['MRP']
            self.Gst = q2[0]['GSTPercentage']

            q2=M_GSTHSNCode.objects.filter(id=QueryForGSTAndMRP[0]['GST']).values('GSTPercentage')
            # if(MCItemUnit == 0): 
            #     a=Q(UnitID=MUnit)
            # else:
            #     a=Q(id=MCItemUnit)   
            # q3SelectedUnit=MC_ItemUnits.objects.filter(Item=ItemID,IsDeleted=0).filter( a ).values('BaseUnitQantity')
            # q3NoUnit=MC_ItemUnits.objects.filter(Item=ItemID,IsDeleted=0,UnitID=2).filter( a ).values('BaseUnitQantity')
            
            
        else:
            Gstfun = GSTHsnCodeMaster(ItemID, self.today).GetTodaysGstHsnCode()
            MRPfun = MRPMaster(ItemID,DivisionID,0,self.today).GetTodaysDateMRP()
            self.MRP=float(MRPfun[0]['TodaysMRP'])
            self.GST=float(Gstfun[0]['GST'])
        
        query =M_Parties.objects.filter(id=PartyID).values('PriceList')
        query1=M_PriceList.objects.filter(id=query[0]['PriceList']).values('CalculationPath')
        self.calculationPath=str(query1[0]['CalculationPath']).split(',')
       
    def RateWithGST(self):
      
        
     
        for i in self.calculationPath:
           
            Margin=MarginMaster(self.ItemID,i,self.PartyID,self.today).GetTodaysDateMargin()
           
            Margin=float(Margin[0]['TodaysMargin'])
            GSTRate=self.MRP/(100+Margin)*100;
            RatewithoutGST=GSTRate*100/(100+self.GST)
            self.MRP=round(GSTRate,2)
        
        RateDetails=list()
        RateDetails.append({
            "RatewithGST":round(GSTRate,0),
            "RateWithoutGST": round(RatewithoutGST,0),
        })
        
        
        
        
        return RateDetails
