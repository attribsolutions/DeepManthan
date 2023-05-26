from django.db.models import Q
from django.db.models import Max
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
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

def UnitDropdown(ItemID,PartyForRate,BatchID=0):
    
    UnitDetails = list()
    ItemUnitquery = MC_ItemUnits.objects.filter(
        Item=ItemID, IsDeleted=0)
    ItemUnitqueryserialize = ItemUnitSerializer(
        ItemUnitquery, many=True).data
   
    RateMcItemUnit = "" 
    q= M_Parties.objects.filter(id=PartyForRate).select_related("PartyType").values("PartyType__IsSCM")
   
    for d in ItemUnitqueryserialize:
        if (d['PODefaultUnit'] == True):
            RateMcItemUnit = d['id']
        if(q[0]['PartyType__IsSCM'] == 1):
            CalculatedRateusingMRPMargin=RateCalculationFunction(0,ItemID,PartyForRate,0,0,d['id']).RateWithGST()
            Rate=CalculatedRateusingMRPMargin[0]["RateWithoutGST"]
        else:
            Rate=0
        UnitDetails.append({
            "UnitID": d['id'],
            "UnitName": d['BaseUnitConversion'] ,
            "BaseUnitQuantity": d['BaseUnitQuantity'],
            "PODefaultUnit": d['PODefaultUnit'],
            "SODefaultUnit": d['SODefaultUnit'],
            "Rate" : Rate

        })
    return UnitDetails




class GetOpeningBalanceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                OpeningBalancedata = JSONParser().parse(request)
                Party = OpeningBalancedata['PartyID']
                Customer = OpeningBalancedata['CustomerID']
                ReceiptDate = OpeningBalancedata['ReceiptDate']
                today = date.today()
        
                query = MC_PartySubPartyOpeningBalance.objects.filter(Party=Party,SubParty=Customer,Year=today.year).values('OpeningBalanceAmount')
               
                if query:
                    OpeningBalanceAmt = query[0]['OpeningBalanceAmount']
                else:
                    OpeningBalanceAmt = 0
                query2 = T_Invoices.objects.raw(''' SELECT '0' id, TransactionDate, InvoiceAmount, ReceiptAmount FROM ( SELECT T_Invoices.InvoiceDate AS TransactionDate, T_Invoices.GrandTotal AS InvoiceAmount, 0 AS ReceiptAmount FROM T_Invoices WHERE T_Invoices.Party_id=%s AND T_Invoices.Customer_id =%s  AND InvoiceDate <= %s  UNION ALL SELECT T_Receipts.ReceiptDate AS TransactionDate, 0 AS InvoiceAmount,T_Receipts.AmountPaid AS ReceiptAmount FROM T_Receipts WHERE  T_Receipts.Party_id=%s AND T_Receipts.Customer_id = %s AND T_Receipts.ReceiptDate <= %s  AND T_Receipts.ReceiptMode_id!=36 AND T_Receipts.ReceiptType_id=29  UNION ALL SELECT T_CreditDebitNotes.CRDRNoteDate AS TransactionDate,(CASE WHEN T_CreditDebitNotes.NoteType_id in (38,40) THEN T_CreditDebitNotes.GrandTotal End) AS InvoiceAmount , (CASE WHEN T_CreditDebitNotes.NoteType_id in (37,39) THEN T_CreditDebitNotes.GrandTotal End) ReceiptAmount FROM T_CreditDebitNotes WHERE T_CreditDebitNotes.Party_id=%s AND T_CreditDebitNotes.Customer_id = %s  AND T_CreditDebitNotes.CRDRNoteDate <= %s ) A   Order By TransactionDate ''', ([Party], [Customer], [ReceiptDate ], [Party], [Customer], [ReceiptDate ], [Party], [Customer], [ReceiptDate]))
                # print(str(query2.query))
                query2_serializer = OpeningBalanceSerializer(query2, many=True).data
                OpeningBalance = 0.000
                InvoiceAmount=0.000
                ReceiptAmount=0.000
                
                for a in query2_serializer:
                    InvoiceAmount = InvoiceAmount + float(a['InvoiceAmount'] or 0)
                    ReceiptAmount = ReceiptAmount + float(a['ReceiptAmount'] or 0)
                # print(self.OpeningBalanceAmt,InvoiceAmount,ReceiptAmount)
                
                OpeningBalance = (float(OpeningBalanceAmt) + InvoiceAmount) - ReceiptAmount
                aa = list()
                aa.append({"OpeningBalanceAmount": OpeningBalance })
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': '', 'Data': aa[0]})
        except Exception as e:
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 


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
                "TodaysMRP":0,
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
            EffectiveDateID = 0
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
            # print(ItemMargindata.query)
        
        
       

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
                "TodaysMargin":0,
                "Date": 0,
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
            EffectiveDateMargin = 0
                
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
            
            q2=M_GSTHSNCode.objects.filter(id=QueryForGSTAndMRP[0]['GST']).values('GSTPercentage')
            self.Gst = q2[0]['GSTPercentage']
        else:
            Gstfun = GSTHsnCodeMaster(ItemID, self.today).GetTodaysGstHsnCode()
            MRPfun = MRPMaster(ItemID,DivisionID,0,self.today).GetTodaysDateMRP()
            # print('MRPfun',MRPfun[0]['TodaysMRP'])
            # print('Gstfun',Gstfun[0]['GST'])
            # print('unitfun',MCItemUnit)
            self.MRP=float(MRPfun[0]['TodaysMRP'])
            self.GST=float(Gstfun[0]['GST'])
        
        
        if(MCItemUnit == 0): 
                a=Q(UnitID=MUnit)
        else:
                a=Q(id=MCItemUnit)   
            
        q3SelectedUnit=MC_ItemUnits.objects.filter(Item=ItemID,IsDeleted=0).filter( a ).values('BaseUnitQuantity')
       
        q3NoUnit=MC_ItemUnits.objects.filter(Item=ItemID,IsDeleted=0,UnitID=1).values('BaseUnitQuantity')
        
        query =M_Parties.objects.filter(id=PartyID).values('PriceList')
        # print(PartyID,query)
        query1=M_PriceList.objects.filter(id=query[0]['PriceList']).values('CalculationPath')
        # print(str(query1.query))
        self.calculationPath=str(query1[0]['CalculationPath']).split(',')
        self.BaseUnitQantityofselectedunit=q3SelectedUnit[0]['BaseUnitQuantity']
        self.BaseUnitQantityofNoUnit= q3NoUnit[0]['BaseUnitQuantity']
    def RateWithGST(self):
      
        for i in self.calculationPath:
           
            Margin=MarginMaster(self.ItemID,i,self.PartyID,self.today).GetTodaysDateMargin()
            # print('Margin',Margin[0]['TodaysMargin'])
            Margin=float(Margin[0]['TodaysMargin'])
            GSTRate=self.MRP/(100+Margin)*100;
            RatewithoutGST=GSTRate*100/(100+self.GST)
            self.MRP=round(GSTRate,2)
        
        RatewithGST=round((float(self.BaseUnitQantityofselectedunit/self.BaseUnitQantityofNoUnit)* float(GSTRate) ),2)
        RateWithoutGST=round((float(self.BaseUnitQantityofselectedunit/self.BaseUnitQantityofNoUnit)* float(RatewithoutGST) ),2)
        
        RateDetails=list()
        RateDetails.append({
            "RatewithGST":RatewithGST,
            "RateWithoutGST": RateWithoutGST,
        })
        
        
        
        
        return RateDetails


 
class GetPartyAddressDetails:
    
    def __init__(self,PartyID):
        self.PartyID = PartyID
            
        
    def PartyAddress(self):     
        
        query = MC_PartyAddress.objects.filter(Party=self.PartyID,IsDefault=1).values('Address','FSSAINo','FSSAIExipry','PIN')
        Address=query[0]['Address']
        FSSAINo=query[0]['FSSAINo']
        FSSAIExipry=query[0]['FSSAIExipry']
        Pin=query[0]['PIN']

        
        Details=list()
        Details.append({
            "Address":Address,
            "FSSAINo": FSSAINo,
            "FSSAIExipry":FSSAIExipry,
            "Pin":Pin
        })
        
    
        return Details        
        
        
        
        
 
        
