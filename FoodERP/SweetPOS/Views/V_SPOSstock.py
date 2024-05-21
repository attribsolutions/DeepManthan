from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from FoodERPApp.Views.V_CommFunction import UnitwiseQuantityConversion, create_transaction_logNew
from FoodERPApp.models import *
from FoodERPApp.Serializer.S_PartyItems import *
from FoodERPApp.Serializer.S_Orders import *
from ..models import  *
from SweetPOS.Serializer.S_SPOSstock import SPOSstockSerializer
from django.db.models import *
from FoodERPApp.Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from datetime import date

class FranchiseStockView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        FranchiseStockdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = FranchiseStockdata['PartyID']
                CreatedBy = FranchiseStockdata['CreatedBy']
                StockDate = FranchiseStockdata['Date']
                Mode =  FranchiseStockdata['Mode']
                IsStockAdjustment=FranchiseStockdata['IsStockAdjustment']
                IsAllStockZero = FranchiseStockdata['IsAllStockZero']

                T_StockEntryList = list()
                Stock_serializer = SPOSstockSerializer(data=FranchiseStockdata, many=True)

                for a in FranchiseStockdata['StockItems']:
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], Party,0)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    Item=a['Item']
                    if Mode == 2:
                        query3 = T_SPOSStock.objects.filter(Party=Party).aggregate(total=Sum('BaseUnitQuantity'))
                    else:
                        query3 = T_SPOSStock.objects.filter(Party=Party,id=a['BatchCodeID']).aggregate(total=Sum('BaseUnitQuantity'))

                    if query3['total']:
                        totalstock=float(query3['total'])
                    else:
                        totalstock=0

                    a['BatchCode'] = BatchCode
                    a['StockDate'] = date.today()
                    a['BaseUnitQuantity'] = round(BaseUnitQuantity,3)

                    T_StockEntryList.append({
                    "StockDate":StockDate,    
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": round(BaseUnitQuantity,3),
                    "MRPValue" :a["MRPValue"],
                    "MRP": a['MRP'],
                    "Party": Party,
                    "CreatedBy":CreatedBy,
                    "BatchCode" : a['BatchCode'],
                    "BatchCodeID" : a['BatchCodeID'],
                    "IsSaleable" : 1,
                    "Difference" : round(BaseUnitQuantity,3)-totalstock,
                    "IsStockAdjustment" : IsStockAdjustment
                    })
                Stock_serializer = SPOSstockSerializer(data=T_StockEntryList, many=True)
                
                if Stock_serializer.is_valid():
                    Stock_serializer.save()
                  
                    log_entry = create_transaction_logNew(request, FranchiseStockdata, FranchiseStockdata['PartyID'],'',381,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, FranchiseStockdata, 0,'FranchiseStockEntrySave:'+str(Stock_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Stock_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, FranchiseStockdata, 0,'FranchiseStockEntrySave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data': []})

class FranchiseItemView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        Logindata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UserID = Logindata['UserID']
                RoleID = Logindata['RoleID']
                CompanyID = Logindata['CompanyID']
                PartyID = Logindata['PartyID']
                CompanyGroupID = Logindata['CompanyGroup']
                IsSCMCompany = Logindata['IsSCMCompany']

                FranchiseItemsList = []
                
                if IsSCMCompany == 1:
                    Itemquery = MC_PartyItems.objects.raw('''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,M_ItemMappingMaster.MapItem FROM M_Items JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  LEFT JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s LEFT JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id LEFT JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id left join M_ItemMappingMaster on M_Items.id=M_ItemMappingMaster.Item_id and M_ItemMappingMaster.Party_id=%s WHERE IsSCM=1 AND M_Items.Company_id IN (select id from C_Companies where CompanyGroup_id=%s) AND M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id FROM MC_PartySubParty JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id WHERE (MC_PartySubParty.Party_id=%s OR SubParty_id=%s))  order by M_Group.id, MC_SubGroup.id ''', ([PartyID], [PartyID], [CompanyGroupID], [PartyID], [PartyID]))
                else:
                    Itemquery = MC_PartyItems.objects.raw('''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,M_ItemMappingMaster.MapItem FROM M_Items JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  LEFT JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s LEFT JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id LEFT JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id left join M_ItemMappingMaster on M_Items.id=M_ItemMappingMaster.Item_id and M_ItemMappingMaster.Party_id=%s WHERE  M_Items.Company_id IN (select id from C_Companies where CompanyGroup_id=%s) AND M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id FROM MC_PartySubParty JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id WHERE (MC_PartySubParty.Party_id=%s OR SubParty_id=%s)) AND MC_PartyItems.Party_id IS NOT NULL order by M_Group.id, MC_SubGroup.id ''', ([PartyID], [PartyID], [CompanyGroupID], [PartyID], [PartyID]))
                if not Itemquery:
                    log_entry = create_transaction_logNew(request, Logindata, 0, 'Items Not available', 181, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available', 'Data': []})
                else:
                    Items_Serializer = MC_PartyItemSerializerSingleGet(Itemquery, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        query1 = M_Items.objects.raw('''select id ,name ,
                                                round(GetTodaysDateMRP(%s,curdate(),2,0,0),2)MRPValue,                                                
                                                round(GetTodaysDateRate(%s,curdate(),0,0,2),2)RateValue,
                                                round(GSTHsnCodeMaster(%s,curdate(),2),2)GSTPercentage,
                                                GetTodaysDateMRP(%s,curdate(),1,0,0)MRPID,
                                                GSTHsnCodeMaster(%s,curdate(),1)GSTID,
                                                GetTodaysDateRate(%s,curdate(),0,0,1)RateID
                                                from M_Items where id =%s''', [a['id'], a['id'], a['id'], a['id'], a['id'], a['id'], a['id']])
                        for b in query1:
                            ItemMRPDetails = [{
                                "MRP": b.MRPID,
                                "MRPValue": b.MRPValue,
                            }]
                            ItemRateDetails = [{
                                "Rate": b.RateID,
                                "RateValue": b.RateValue,
                            }]
                            ItemGSTDetails = [{
                                "GST": b.GSTID,
                                "GSTPercentage": b.GSTPercentage,
                            }]
                            Unitquery = MC_ItemUnits.objects.filter(Item_id=b.id, IsDeleted=0)
                            if Unitquery.exists():
                                Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                                ItemUnitDetails = []
                                for c in Unitdata:
                                    ItemUnitDetails = [{
                                        "Unit": c['id'],
                                        "BaseUnitQuantity": c['BaseUnitQuantity'],
                                        "IsBase": c['IsBase'],
                                        "UnitName": c['BaseUnitConversion'],
                                    }]
                            else:
                                ItemUnitDetails = []

                            FranchiseItemsList.append({
                                "Item": a['id'],
                                "ItemName": a['Name'],
                                "ItemUnitDetails": ItemUnitDetails,
                                "ItemMRPDetails": ItemMRPDetails,
                                "ItemGSTDetails": ItemGSTDetails,
                                "ItemRateDetails": ItemRateDetails
                            })

                    ItemList.append({"InvoiceItems":FranchiseItemsList})        
                log_entry = create_transaction_logNew(request, Logindata, PartyID, '', 181, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Logindata, 0, 'FetchSingleGETItem:' + str(Exception(e)), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})




