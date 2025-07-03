from django.db.models import Q
from django.db.models import Max
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from FoodERPDBLog.views import create_transaction_logNew2
from ..Serializer.S_CommFunction import *
from ..Serializer.S_Mrps import *
from ..Serializer.S_Margins import *
from ..Serializer.S_GSTHSNCode import *
from ..Serializer.S_GSTHSNCode import *
from ..models import *
from datetime import date
from ..models import TransactionLogJsonData
from ..models import M_Settings
from django.db import connection
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from django.contrib.auth import authenticate
import base64
import os
from rest_framework import status


'''Common Functions List
1) class MaxValueMaster -  GetMaxValue
2) class MRPMaster - GetTodaysDateMRP, GetEffectiveDateMRP, GetEffectiveDateMRPID
3) class MarginMaster - GetTodaysDateMargin, GetEffectiveDateMargin, GetEffectiveDateMarginID
4) class GSTHsnCodeMaster - GetTodaysGstHsnCode, GetEffectiveDateGSTHSNCode, GetEffectiveDateGSTHSNCodeID
5) class UnitwiseQuantityConversion - GetBaseUnitQuantity, ConvertintoSelectedUnit
6) class ShowBaseUnitQtyOnUnitDropDown - ShowDetails(baseunitname), TrimQty(Baseunitqty)
7) class UnitwiseQuantityConversion - GetBaseUnitQuantity,ConvertintoSelectedUnit
8) class ShowBaseUnitQtyOnUnitDropDown -ShowDetails
9)Skygge Third Party API - Product


'''


def GetThirdPartyAPIs(id):

    url_query = M_Settings.objects.filter(id=id).values('DefaultValue')
    URL = url_query[0]['DefaultValue']
    # Token only For Skygge APIs
    token_query = M_Settings.objects.filter(id=24).values('DefaultValue')

    Token = token_query[0]['DefaultValue']

    return URL, Token


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_transaction_log(request, data, User, PartyID, TransactionDetails, TransactionType=0, TransactionID=0):

    log_entry = Transactionlog.objects.create(
        TranasactionDate=date.today(),
        User=User, PartyID=PartyID, IPaddress=get_client_ip(request), TransactionDetails=TransactionDetails, JsonData=data, TransactionType=TransactionType, TransactionID=TransactionID
    )
    return log_entry


def create_transaction_logNew(request, data, PartyID, TransactionDetails, TransactionType=0, TransactionID=0, FromDate=0, ToDate=0, CustomerID=0):
    log_entry=create_transaction_logNew2(request, data, PartyID, TransactionDetails, TransactionType, TransactionID, FromDate, ToDate, CustomerID)
    # Authenticated_User = request.user
    # User = Authenticated_User.id
    # aa = M_Settings.objects.filter(id=31).values('DefaultValue')

    # if aa[0]['DefaultValue'] == "1":
    #     if not User:
    #         User = data['UserID']
    #     else:
    #         pass

    #     if not FromDate:
    #         log_entry = Transactionlog.objects.create(TranasactionDate=date.today(), User=User, PartyID=PartyID, IPaddress=get_client_ip(
    #             request), TransactionDetails=TransactionDetails, JsonData=0, TransactionType=TransactionType, TransactionID=TransactionID, CustomerID=CustomerID)
    #     else:
    #         log_entry = Transactionlog.objects.create(TranasactionDate=date.today(), User=User, PartyID=PartyID, IPaddress=get_client_ip(
    #             request), TransactionDetails=TransactionDetails, JsonData=0, TransactionType=TransactionType, TransactionID=TransactionID, FromDate=FromDate, ToDate=ToDate, CustomerID=CustomerID)

    #     TransactionLogJsonData.objects.create(
    #         Transactionlog=log_entry, JsonData=data)

    #     return log_entry

    # else:
    #     return None
    return log_entry
    
def MRPListFun(Item,Party,PartyType):
    PartyTypeQuery=M_Parties.objects.filter(id=Party).values('PartyType')
    if PartyType: 
        PartyTypeID=PartyType 
    else:
        PartyTypeID= PartyTypeQuery[0]['PartyType']
    MRPquery = M_MRPMaster.objects.filter(Item_id=Item,Party=Party,PartyType__isnull=True,IsDeleted=0).values('MRP','id').order_by('-id')
    if not MRPquery:
        MRPquery = M_MRPMaster.objects.filter(Item_id=Item,Party__isnull=True,PartyType=PartyTypeID,IsDeleted=0).values('MRP','id').order_by('-id')
        if not MRPquery:
            MRPquery = M_MRPMaster.objects.filter(Item_id=Item,Party__isnull=True,PartyType__isnull=True,IsDeleted=0).values('MRP','id').order_by('-id')
    return MRPquery

def GSTListFun(Item,Party,PartyType):
    PartyTypeQuery=M_Parties.objects.filter(id=Party).values('PartyType')
    if PartyType: 
        PartyTypeID=PartyType 
    else:
        PartyTypeID= PartyTypeQuery[0]['PartyType']
    GSTquery =M_GSTHSNCode.objects.filter(Item_id=Item,PartyType=PartyTypeID).values('GSTPercentage','id','HSNCode').order_by('-id')[:3]
    if not GSTquery:
        GSTquery =M_GSTHSNCode.objects.filter(Item_id=Item,PartyType__isnull=True).values('GSTPercentage','id','HSNCode').order_by('-id')[:3]
    
    return GSTquery
def UnitDropdown(ItemID, PartyForRate, BatchID=0):   
    UnitDetails = list()
    ItemUnitquery = MC_ItemUnits.objects.filter(Item=ItemID, IsDeleted=0,IsShowUnit=1).select_related('UnitID').values('id','BaseUnitQuantity','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion','UnitID__id')
    # Same Base Unit Quantity then show Only BaseUnit
    # ItemUnitquery2 = MC_ItemUnits.objects.filter(Item=ItemID, IsDeleted=0 ,IsBase=1).select_related('UnitID').values('id','BaseUnitQuantity','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion','UnitID__id')
    # BaseUnitQuantity=ItemUnitquery2[0]['BaseUnitQuantity']    
    # UnitID_List=[]
    # for unit in ItemUnitquery:
    #     UnitQuantity=unit['BaseUnitQuantity']
 
    #     Base=unit['IsBase']         
    #     if  Base==False:               
    #         if(BaseUnitQuantity ==UnitQuantity):
    #             UnitID_List.append(str(unit['id']))  
    # ItemUnitquery = MC_ItemUnits.objects.filter(Item=ItemID, IsDeleted=0 ).exclude(
    # id__in=UnitID_List).select_related('UnitID').values('id','BaseUnitQuantity','IsBase','PODefaultUnit','SODefaultUnit','BaseUnitConversion','UnitID__id')
 
    
    
    q1 = M_Parties.objects.filter(id=PartyForRate ).values("PartyType_id")
    PartyTypeID=q1[0]['PartyType_id']
    
    Q11=M_Settings.objects.filter(id=44).values("DefaultValue")
    PartyTypeID1=str(Q11[0]['DefaultValue'])
    PartyTypeID1_list = [int(x) for x in PartyTypeID1.split(",")]
    
    for d in ItemUnitquery:
       
        # if (d['PODefaultUnit'] == True):
        RateMcItemUnit = d['id']
        
        if PartyTypeID in PartyTypeID1_list:
            
            query2 = M_MarginMaster.objects.raw(f'''select 1 as id, RateCalculationFunction1(0,{ItemID}, {PartyForRate},1, 0, 0, 0, 0)RatewithoutGST''')
            
            # CalculatedRateusingMRPMargin = RateCalculationFunction(
            #     0, ItemID, PartyForRate, 0, 0, d['id'], 0).RateWithGST()
            # Rate = CalculatedRateusingMRPMargin[0]["NoRatewithOutGST"]
            
            if query2:
                rate_without_gst = query2[0].RatewithoutGST
                if rate_without_gst is not None:
                    Rate = round(float(rate_without_gst), 2)                    
                else:
                    Rate=0.0
            else:
                Rate = 0.0
        else:
            Rate=0.0

        q0 = MC_ItemUnits.objects.filter(
            Item=ItemID, UnitID=1, IsDeleted=0).values("BaseUnitQuantity")
     
        UnitDetails.append({
            "UnitID": d['id'],
            "UnitName": d['BaseUnitConversion'],
            "BaseUnitQuantity": d['BaseUnitQuantity'],
            "PODefaultUnit": d['PODefaultUnit'],
            "SODefaultUnit": d['SODefaultUnit'],
            # "Rate": round(Rate, 2),
            "Rate" : Rate,
            "BaseUnitQuantityNoUnit": q0[0]["BaseUnitQuantity"],
            "DeletedMCUnitsUnitID": d['UnitID__id'],
            "IsBase" : d['IsBase']

        })
    return UnitDetails


def GetOpeningBalance(Party, Customer, Date):
    # today = date.today()
    # query = MC_PartySubPartyOpeningBalance.objects.filter(
    #     Party=Party, SubParty=Customer, Year=today.year).values('OpeningBalanceAmount')

    # if query:
    #     OpeningBalanceAmt = query[0]['OpeningBalanceAmount']
    # else:
    #     OpeningBalanceAmt = 0
    query2 = T_Invoices.objects.raw(''' SELECT id, TransactionDate, InvoiceAmount, ReceiptAmount FROM 
    ( SELECT 1 as id ,Date AS TransactionDate, 
    OpeningBalanceAmount AS InvoiceAmount,
    0 AS ReceiptAmount
    FROM MC_PartySubPartyOpeningBalance 
    WHERE Party_id=%s AND SubParty_id =%s  AND Date <= %s
    
    UNION ALL
        
    SELECT 2 as id ,T_Invoices.InvoiceDate AS TransactionDate, T_Invoices.GrandTotal AS InvoiceAmount, 0 AS ReceiptAmount 
    FROM T_Invoices WHERE T_Invoices.Party_id=%s AND T_Invoices.Customer_id =%s  AND InvoiceDate <= %s  
    UNION ALL 
    
    SELECT 3 as id ,T_Receipts.ReceiptDate AS TransactionDate, 0 AS InvoiceAmount,T_Receipts.AmountPaid AS ReceiptAmount 
    FROM T_Receipts WHERE  T_Receipts.Party_id=%s AND T_Receipts.Customer_id = %s AND T_Receipts.ReceiptDate <= %s  AND T_Receipts.ReceiptMode_id!=36 AND T_Receipts.ReceiptType_id=29  
    UNION ALL 
    
    SELECT 4 as id ,T_CreditDebitNotes.CRDRNoteDate AS TransactionDate,(CASE WHEN T_CreditDebitNotes.NoteType_id in (38,40) THEN T_CreditDebitNotes.GrandTotal else 0 End) AS InvoiceAmount ,
    (CASE WHEN T_CreditDebitNotes.NoteType_id in (37,39) THEN T_CreditDebitNotes.GrandTotal else 0 End) ReceiptAmount FROM T_CreditDebitNotes WHERE T_CreditDebitNotes.Party_id=%s AND T_CreditDebitNotes.Customer_id = %s  AND T_CreditDebitNotes.CRDRNoteDate <= %s and IsDeleted=0 ) A   Order By TransactionDate ''', ([
                                    Party], [Customer], [Date],[Party], [Customer], [Date], [Party], [Customer], [Date], [Party], [Customer], [Date]))
   
    query2_serializer = OpeningBalanceSerializer(query2, many=True).data
    OpeningBalance = 0.000
    InvoiceAmount = 0.000
    ReceiptAmount = 0.000
    
    for a in query2_serializer:
        
        InvoiceAmount =  float(a['InvoiceAmount'] or 0)
        ReceiptAmount =  float(a['ReceiptAmount'] or 0)
        if a['id'] == 1:
            OpeningBalance = 0
        
        
        OpeningBalance = (float(OpeningBalance) + InvoiceAmount) - ReceiptAmount
        

    # OpeningBalance = (float(OpeningBalanceAmt) + InvoiceAmount) - ReceiptAmount
    return OpeningBalance


class GetOpeningBalanceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        OpeningBalancedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = OpeningBalancedata['PartyID']
                Customer = OpeningBalancedata['CustomerID']
                ReceiptDate = OpeningBalancedata['ReceiptDate']
                today = date.today()

                OpeningBalance = GetOpeningBalance(
                    Party, Customer, ReceiptDate)
                aa = list()
                aa.append({"OpeningBalanceAmount": OpeningBalance})
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': '', 'Data': aa[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


def GetO_BatchWiseLiveStock(ItemID, PartyID):

    items = O_BatchWiseLiveStock.objects.filter(Item=ItemID, Party=PartyID)
    total_Stock = sum(items.values_list('BaseUnitQuantity', flat=True))

    return total_Stock


class MaxValueMaster:

    def __init__(self, TableName, ColumnName):
        self.TableName = TableName
        self.ColumnName = ColumnName

    def GetMaxValue(self):
        MaxCommonID = self.TableName.objects.aggregate(Max(self.ColumnName))
        a = MaxCommonID['CommonID__max']
        if a is None:
            a = 1
        else:
            a = a+1
        return a


class MRPMaster:

    today = date.today()

    def __init__(self, ItemID, DivisionID, PartyID, EffectiveDate):
        self.ItemID = ItemID
        self.DivisionID = DivisionID
        self.PartyID = PartyID
        self.EffectiveDate = EffectiveDate

    def GetTodaysDateMRP(self):
        if int(self.DivisionID) > 0:
            D = Q(Division_id=self.DivisionID)
        else:
            D = Q(Division_id__isnull=True)

        if int(self.PartyID) > 0:
            P = Q(Party_id=self.PartyID)
        else:
            P = Q(Party_id__isnull=True)

        TodayDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(
            Item_id=self.ItemID, EffectiveDate__lte=self.today, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
       

        if TodayDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(
                TodayDateItemMRPdata, many=True).data
            Mrpid = MRP_Serializer[0]['id']
            MRPs = MRP_Serializer[0]['MRP']
            Date = MRP_Serializer[0]['EffectiveDate']
            MRPDetails = list()
            MRPDetails.append({
                "TodaysMRP": MRPs,
                "Date": Date,
                "Mrpid": Mrpid
            })
        else:
            MRPDetails = list()
            MRPDetails.append({
                "TodaysMRP": 0,
                "Date": "",
                "Mrpid": ""
            })

        return MRPDetails

    def GetEffectiveDateMRP(self):
        if int(self.DivisionID) > 0:
            D = Q(Division_id=self.DivisionID)
        else:
            D = Q(Division_id__isnull=True)

        if int(self.PartyID) > 0:
            P = Q(Party_id=self.PartyID)
        else:
            P = Q(Party_id__isnull=True)

        EffectiveDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(
            Item_id=self.ItemID, EffectiveDate=self.EffectiveDate, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
      

        if EffectiveDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(
                EffectiveDateItemMRPdata, many=True).data
            EffectiveDateMRP = MRP_Serializer[0]['MRP']
        else:
            EffectiveDateMRP = ""
        return EffectiveDateMRP

    def GetEffectiveDateMRPID(self):
        if int(self.DivisionID) > 0:
            D = Q(Division_id=self.DivisionID)
        else:
            D = Q(Division_id__isnull=True)

        if int(self.PartyID) > 0:
            P = Q(Party_id=self.PartyID)
        else:
            P = Q(Party_id__isnull=True)

        EffectiveDateItemMRPdata = M_MRPMaster.objects.filter(P & D).filter(
            Item_id=self.ItemID, EffectiveDate=self.EffectiveDate, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]

        if EffectiveDateItemMRPdata.exists():
            MRP_Serializer = M_MRPsSerializer(
                EffectiveDateItemMRPdata, many=True).data
            EffectiveDateID = MRP_Serializer[0]['id']
        else:
            EffectiveDateID = 0
        return EffectiveDateID

###################################################################################################################


class DiscountMaster:

    today = date.today()

    def __init__(self, ItemID, PartyID, EffectiveDate, Customer=0, PriceListID=0):
        self.ItemID = ItemID
        self.PriceListID = PriceListID
        self.PartyID = PartyID
        self.EffectiveDate = EffectiveDate
        self.Customer = Customer

        pricelistquery = M_Parties.objects.filter(
            id=Customer).values("PriceList")
        self.PriceListID = pricelistquery[0]["PriceList"]

    def GetTodaysDateDiscount(self):

        if int(self.Customer) > 0:
            P = Q(Customer=self.Customer)
        else:
            P = Q()

        D = Q(FromDate__lte=self.EffectiveDate) & Q(
            ToDate__gte=self.EffectiveDate)
        ItemDiscountdata = M_DiscountMaster.objects.filter(Item_id=self.ItemID, PriceList_id=self.PriceListID, Party=self.PartyID, IsDeleted=0).filter(
            D).filter(P).values("DiscountType", "Discount").order_by('-id')[:1]
    
        if not ItemDiscountdata:

            ItemDiscountdata = M_DiscountMaster.objects.filter(Item_id=self.ItemID, PriceList_id=self.PriceListID, Party=self.PartyID, Customer_id__isnull=True, IsDeleted=0).filter(
                D).values("DiscountType", "Discount").order_by('-id')[:1]

        if ItemDiscountdata:
            DiscountDetails = list()
            DiscountDetails.append({
                "TodaysDiscount": ItemDiscountdata[0]["Discount"],
                "DiscountType": ItemDiscountdata[0]["DiscountType"],

            })
        else:
            DiscountDetails = list()
            DiscountDetails.append({
                "TodaysDiscount": "",
                "DiscountType": "",

            })

        return DiscountDetails

###################################################################################################################


class MarginMaster:

    today = date.today()

    def __init__(self, ItemID, PriceListID, PartyID, EffectiveDate):
        self.ItemID = ItemID
        self.PriceListID = PriceListID
        self.PartyID = PartyID
        self.EffectiveDate = EffectiveDate

    def GetTodaysDateMargin(self):

        if int(self.PartyID) > 0:
            P = Q(Party_id=self.PartyID)
        else:
            P = Q(Party_id__isnull=True)

        ItemMargindata = M_MarginMaster.objects.filter(P).filter(
            Item_id=self.ItemID, PriceList_id=self.PriceListID, EffectiveDate__lte=self.today, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
      
        if ItemMargindata.exists:

            P = Q(Party_id__isnull=True)
            ItemMargindata = M_MarginMaster.objects.filter(P).filter(
                Item_id=self.ItemID, PriceList_id=self.PriceListID, EffectiveDate__lte=self.today, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
           

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(
                ItemMargindata, many=True).data
            Margin = Margin_Serializer[0]['Margin']
            Date = Margin_Serializer[0]['EffectiveDate']
            MarginDetails = list()
            MarginDetails.append({
                "TodaysMargin": Margin,
                "Date": Date,
            })

        else:
            MarginDetails = list()
            MarginDetails.append({
                "TodaysMargin": 0,
                "Date": 0,
            })

        return MarginDetails

    def GetEffectiveDateMargin(self):

        if int(self.PartyID) > 0:
            P = Q(Party_id=self.PartyID)
        else:
            P = Q(Party_id__isnull=True)

        ItemMargindata = M_MarginMaster.objects.filter(P).filter(
            Item_id=self.ItemID, PriceList_id=self.PriceListID, EffectiveDate=self.EffectiveDate, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
       
        # if ItemMargindata.count() == 0:
        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(
                ItemMargindata, many=True).data
            EffectiveDateMargin = Margin_Serializer[0]['Margin']
        else:
            EffectiveDateMargin = 0

        return EffectiveDateMargin

    def GetEffectiveDateMarginID(self):

        if int(self.PartyID) > 0:
            P = Q(Party_id=self.PartyID)
        else:
            P = Q(Party_id__isnull=True)

        ItemMargindata = M_MarginMaster.objects.filter(P).filter(
            Item_id=self.ItemID, PriceList_id=self.PriceListID, EffectiveDate=self.EffectiveDate, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
     

        if ItemMargindata.exists():
            Margin_Serializer = M_MarginsSerializer(
                ItemMargindata, many=True).data
            EffectiveDateMarginID = Margin_Serializer[0]['id']
        else:
            EffectiveDateMarginID = ""

        return EffectiveDateMarginID


class GSTHsnCodeMaster:

    today = date.today()

    def __init__(self, ItemID, EffectiveDate):
        self.ItemID = ItemID
        self.EffectiveDate = EffectiveDate

    def GetTodaysGstHsnCode(self):

        TodayDateGstHsncodedata = M_GSTHSNCode.objects.filter(
            Item_id=self.ItemID, EffectiveDate__lte=self.today, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
        if TodayDateGstHsncodedata.exists():
            GSTHsnCode_Serializer = M_GstHsnCodeSerializer(
                TodayDateGstHsncodedata, many=True).data
            Gstid = GSTHsnCode_Serializer[0]['id']
            Gst = GSTHsnCode_Serializer[0]['GSTPercentage']
            HSNCode = GSTHsnCode_Serializer[0]['HSNCode']
            Details = list()
            Details.append({
                "GST": Gst,
                "HSNCode": HSNCode,
                "Gstid": Gstid
            })

        else:
            Details = list()
            Details.append({
                "GST": "",
                "HSNCode": "",
                "Gstid": ""
            })

        return Details

    def GetEffectiveDateGstHsnCode(self):
        EffectiveDateGstHsnCodedata = M_GSTHSNCode.objects.filter(
            Item_id=self.ItemID, EffectiveDate=self.EffectiveDate, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
        if EffectiveDateGstHsnCodedata.exists():
            GSTHsnCode_Serializer = M_GstHsnCodeSerializer(
                EffectiveDateGstHsnCodedata, many=True).data
            Gst = GSTHsnCode_Serializer[0]['GSTPercentage']
            HSNCode = GSTHsnCode_Serializer[0]['HSNCode']
            Details = list()
            Details.append({
                "GST": Gst,
                "HSNCode": HSNCode,
            })

        else:
            Details = list()
            Details.append({
                "GST": "",
                "HSNCode": "",
            })
        return Details

    def GetEffectiveDateGstHsnID(self):

        EffectiveDateGstHsndata = M_GSTHSNCode.objects.filter(
            Item_id=self.ItemID, EffectiveDate=self.EffectiveDate, IsDeleted=0).order_by('-EffectiveDate', '-id')[:1]
        if EffectiveDateGstHsndata.exists():
            GstHsnCode_Serializer = M_GstHsnCodeSerializer(
                EffectiveDateGstHsndata, many=True).data
            EffectiveDateID = GstHsnCode_Serializer[0]['id']
        else:
            EffectiveDateID = ""
        return EffectiveDateID


class UnitwiseQuantityConversion:

    def __init__(self, ItemID, InputQuantity, MCItemUnit, MUnits, ConversionMCItemUnit, ConversionMUnits, ShowDeletedUnitAlso):
        self.ItemID = ItemID
        self.InputQuantity = InputQuantity
        self.MCItemUnit = MCItemUnit
        self.MUnits = MUnits
        self.ConversionMCItemUnit = ConversionMCItemUnit
        self.ConversionMUnits = ConversionMUnits
        self.ShowDeletedUnitAlso = ShowDeletedUnitAlso

        if(ShowDeletedUnitAlso == 1):
            aaa = Q()
        else:
            aaa = Q(IsDeleted=0)
        if(MCItemUnit == 0 & MUnits == 0):
            BaseUnitQuantityQuery = MC_ItemUnits.objects.all().filter(
                Item=ItemID, IsBase=1).select_related()
            BaseUnitQuantitySerializer = ItemUnitsSerializer(
                BaseUnitQuantityQuery, many=True).data
            self.BaseUnitQuantity = BaseUnitQuantitySerializer[0]['BaseUnitQuantity']
        else:

            if(MCItemUnit == 0):
                a = Q(UnitID=MUnits)
            else:
                a = Q(id=MCItemUnit)

            BaseUnitQuantityQuery = MC_ItemUnits.objects.all().filter(
                Item=ItemID).filter(a).select_related()  # .filter( aaa )

            BaseUnitQuantitySerializer = ItemUnitsSerializer(
                BaseUnitQuantityQuery, many=True).data
            unitnamequery = M_Units.objects.filter(
                id=BaseUnitQuantitySerializer[0]['UnitID']).select_related().values('Name')
            self.UnitName = unitnamequery[0]['Name']

            self.BaseUnitQuantity = BaseUnitQuantitySerializer[0]['BaseUnitQuantity']

        if(ConversionMCItemUnit != 0) or (ConversionMUnits != 0):
            if(ConversionMCItemUnit == 0):
                b = Q(UnitID=ConversionMUnits)
            else:
                b = Q(id=ConversionMCItemUnit)
            ConversionUnitBaseQuantityQuery = MC_ItemUnits.objects.filter(
                Item=ItemID).filter(b).filter(aaa).select_related()
            if ConversionUnitBaseQuantityQuery.count() > 0:
                ConversionUnitBaseQuantitySerializer = ItemUnitsSerializer(
                    ConversionUnitBaseQuantityQuery, many=True).data
                self.ConversionUnitBaseQuantity = ConversionUnitBaseQuantitySerializer[
                    0]['BaseUnitQuantity']
            else:
                self.ConversionUnitBaseQuantity = 0

    def GetBaseUnitQuantity(self):

        BaseUnitQuantity = float(self.InputQuantity) * \
            float(self.BaseUnitQuantity)

        return BaseUnitQuantity

    def ConvertintoSelectedUnit(self):

        BaseUnitQuantity = float(self.InputQuantity) * \
            float(self.BaseUnitQuantity)
        if float(self.ConversionUnitBaseQuantity) == 0:
            ConvertedQuantity = 0
        else:
            ConvertedQuantity = float(
                BaseUnitQuantity) / float(self.ConversionUnitBaseQuantity)

        return ConvertedQuantity

    def GetConvertingBaseUnitQtyBaseUnitName(self):

        MCItemUnitID = MC_ItemUnits.objects.all().filter(
            Item=self.ItemID, IsBase=1, IsDeleted=0).select_related().values('id')
        if self.MCItemUnit == MCItemUnitID[0]['id']:
            return self.UnitName
        else:
            BaseUnitQuantity = float(
                self.InputQuantity) * float(self.BaseUnitQuantity)
            baseunitqty = round(float(BaseUnitQuantity), 2)
            UnitID = MC_ItemUnits.objects.all().filter(Item=self.ItemID, IsBase=1,
                                                       IsDeleted=0).select_related().values('UnitID')
            BaseUnitName = M_Units.objects.filter(
                id=UnitID[0]['UnitID']).select_related().values('Name')
            # aaa=  self.UnitName+"("+str(baseunitqty)+" "+BaseUnitName[0]['Name']+")"
            aaa = "("+str(baseunitqty)+" "+BaseUnitName[0]['Name']+")"
            return aaa


class RateCalculationFunction:

    def __init__(self, BatchID=0, ItemID=0, PartyID=0, DivisionID=0, MUnit=0, MCItemUnit=0, PriceList=0, selectedMRP=0):
        self.ItemID = ItemID
        self.PartyID = PartyID
        self.BatchID = BatchID
        self.DivisionID = DivisionID
        self.today = date.today()
        self.PriceList = PriceList
        self.selectedMRP = selectedMRP

        if(BatchID > 0):

            QueryForGSTAndMRP = O_LiveBatches.objects.filter(
                id=BatchID).values('MRP', 'GST', 'GSTPercentage', 'MRPValue')
            q1 = M_MRPMaster.objects.filter(
                id=QueryForGSTAndMRP[0]['MRP']).values('MRP')

            if q1.count() > 0:
                self.MRP = q1[0]['MRP']
            else:
                self.MRP = 0

            if(QueryForGSTAndMRP[0]['GST'] is None):

                self.GST = QueryForGSTAndMRP[0]['GSTPercentage']

            else:
                q2 = M_GSTHSNCode.objects.filter(
                    id=QueryForGSTAndMRP[0]['GST']).values('GSTPercentage')

                self.GST = q2[0]['GSTPercentage']

        else:
            Gstfun = GSTHsnCodeMaster(ItemID, self.today).GetTodaysGstHsnCode()
            MRPfun = MRPMaster(ItemID, DivisionID, 0,
                               self.today).GetTodaysDateMRP()
            # CustomPrint('MRPfun',MRPfun[0]['TodaysMRP'])
            # CustomPrint('Gstfun',Gstfun[0]['GST'])
            # CustomPrint('unitfun',MCItemUnit)
            if selectedMRP != 0:
                self.MRP = self.selectedMRP
            else:
                self.MRP = float(MRPfun[0]['TodaysMRP'])

            self.GST = float(Gstfun[0]['GST'])

        if(MCItemUnit == 0):
            a = Q(UnitID=MUnit)
        else:
            a = Q(id=MCItemUnit)

        q3SelectedUnit = MC_ItemUnits.objects.filter(Item=ItemID).filter(
            a).values('BaseUnitQuantity')  # IsDeleted=0

        q3NoUnit = MC_ItemUnits.objects.filter(
            Item=ItemID, IsDeleted=0, UnitID=1).values('BaseUnitQuantity')

        if self.PriceList > 0:
            PriceList = self.PriceList
        else:

            query = M_Parties.objects.filter(id=PartyID).values('PriceList')
            PriceList = query[0]['PriceList']

        query1 = M_PriceList.objects.filter(id=PriceList).values('CalculationPath')
 
        self.calculationPath = str(query1[0]['CalculationPath']).split(',')
        self.BaseUnitQantityofselectedunit = q3SelectedUnit[0]['BaseUnitQuantity']
        self.BaseUnitQantityofNoUnit = q3NoUnit[0]['BaseUnitQuantity']

    def RateWithGST(self):

        for i in self.calculationPath:

            query3 = M_PriceList.objects.filter(id=i).values('MkUpMkDn')

            Margin = MarginMaster(
                self.ItemID, i, self.PartyID, self.today).GetTodaysDateMargin()

            Margin = float(Margin[0]['TodaysMargin'])

            if(query3[0]['MkUpMkDn'] == False):
                GSTRate = float(self.MRP)/(100+Margin)*100
            else:
                GSTRate = float(self.MRP)-(float(self.MRP)*(Margin/100))

            RoundedGSTRate = round(GSTRate, 2)
            RatewithoutGST = float(RoundedGSTRate)*100/(100+float(self.GST))
            self.MRP = round(RoundedGSTRate, 2)

        RatewithGST = round((float(self.BaseUnitQantityofselectedunit /
                            self.BaseUnitQantityofNoUnit) * float(GSTRate)), 2)
        RateWithoutGST = round((float(self.BaseUnitQantityofselectedunit /
                               self.BaseUnitQantityofNoUnit) * float(RatewithoutGST)), 2)

        RateDetails = list()
        RateDetails.append({
            "RatewithGST": RatewithGST,
            "RateWithoutGST": RateWithoutGST,
            "NoRatewithGST": round(RoundedGSTRate, 2),
            "NoRatewithOutGST": round(RatewithoutGST, 2)
        })

        return RateDetails


class GetPartyAddressDetails:

    def __init__(self, PartyID):
        self.PartyID = PartyID

    def PartyAddress(self):

        query = MC_PartyAddress.objects.filter(Party=self.PartyID, IsDefault=1).values(
            'Address', 'FSSAINo', 'FSSAIExipry', 'PIN')
        Address = query[0]['Address']
        FSSAINo = query[0]['FSSAINo']
        FSSAIExipry = query[0]['FSSAIExipry']
        Pin = query[0]['PIN']

        Details = list()
        Details.append({
            "Address": Address,
            "FSSAINo": FSSAINo,
            "FSSAIExipry": FSSAIExipry,
            "Pin": Pin
        })

        return Details


def ValidationFunForStockTransactions(PartyID, ItemID, TransactionDate):

    q = L_TransactionDateLog.objects.raw(
        '''select 1 as id,StockAdjustmentDate from L_TransactionDateLog where Item=%s and Party=%s ''', ([ItemID], [PartyID]))
    for row in q:
        StockAdjustmentDate = row.StockAdjustmentDate

   
    if StockAdjustmentDate >= TransactionDate:
        return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Transaction not allowed', 'Data': []})
    else:
        pass


def TransactionDateLogFun(PartyID, ItemID, inputTransactionDate, inputStockAdjustmentDate):
    q = L_TransactionDateLog.objects.raw(
        '''select id,OldestTrnDate,NewestTrnDate,StockAdjustmentDate from L_TransactionDateLog where Item=%s and Party=%s ''', ([ItemID], [PartyID]))

    if q:
        for row in q:
            OldestTrnDate = row.OldestTrnDate
            NewestTrnDate = row.NewestTrnDate
            StockAdjustmentDate = row.StockAdjustmentDate
            if not StockAdjustmentDate:
                pass

    else:
        q1 = L_TransactionDateLog.objects.create(OldestTrnDate=inputTransactionDate, NewestTrnDate=inputTransactionDate,
                                                 StockAdjustmentDate=inputStockAdjustmentDate, Party=PartyID, Item=ItemID)


class LogTransactionView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        LogData = JSONParser().parse(request)
        try:
            PartyID = LogData['PartyID']
            TransactionID = LogData['TransactionID']
            FromDate = LogData['FromDate']
            ToDate = LogData['ToDate']
            CustomerID = LogData['CustomerID']
        
            LogEntry = create_transaction_logNew(request, LogData, PartyID, 'Important Notification', 361, TransactionID, FromDate, ToDate, CustomerID)
            
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': {'LogEntryID': LogEntry.id}})
        except Exception as e:
            transaction.set_rollback(True)  
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': None})



def Get_Items_ByGroupandPartytype(Party ,GroupType=0):
    
    if GroupType > 0:
        GroupType_id = GroupType
        if GroupType_id==5:
            seq = (f'groupdetails.ItemSequence')
        else:
            GroupType_id ==1
            seq=(f'M_Items.Sequence')
    else: 
        party_instance = M_Parties.objects.filter(id=Party).values('PartyType_id')
        
        if party_instance[0]['PartyType_id'] == 19:
            GroupType_id = 5
            seq=(f'groupdetails.ItemSequence')
        else:
            GroupType_id = 1
            seq=(f'M_Items.Sequence')
            
    selects = (f'''ifnull(GroupType.Name,'') GroupTypeName,ifnull(Groupss.Name,'') GroupName,ifnull(subgroup.Name,'') SubGroupName ''')
    
    joins =(f'''LEFT JOIN FoodERP.MC_ItemGroupDetails groupdetails ON groupdetails.item_id = M_Items.id and groupdetails.GroupType_id= {GroupType_id}
        LEFT JOIN FoodERP.M_GroupType GroupType ON GroupType.id = groupdetails.GroupType_id  
        LEFT JOIN FoodERP.M_Group Groupss ON Groupss.id = groupdetails.Group_id
        LEFT JOIN FoodERP.MC_SubGroup subgroup ON subgroup.id = groupdetails.SubGroup_id''')
        
    orderby=(f'''ORDER BY Groupss.Sequence,subgroup.Sequence,{seq}''')
    

    return selects +'!'+ joins +'!'+ orderby


def BasicAuthenticationfunction(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
                    
        # Parsing the authorization header
        auth_type, auth_string = auth_header.split(' ', 1)
        if auth_type.lower() == 'basic':
            
            
            try:
                username, password = base64.b64decode(
                    auth_string).decode().split(':', 1)
            except (TypeError, ValueError, UnicodeDecodeError):
                return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                
        user = authenticate(request, username=username, password=password)
    return user


def get_uploaded_filename(file_field):
    """
    Returns the filename from a Django FileField or ImageField.
    If no file is uploaded, returns None. 
    Args: file_field: The FileField or ImageField instance.
    Returns: str or None: The base filename or None if no file is uploaded.
    """
    if file_field:
        return os.path.basename(file_field.name)
    return None
