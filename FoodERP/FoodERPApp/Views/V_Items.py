from decimal import Decimal
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from rest_framework.parsers import JSONParser
from ..Serializer.S_PriceLists import *
from  ..Serializer.S_Items import *
from  ..Serializer.S_GeneralMaster import *
from ..models import *
from django.db.models import F
from django.db import connections
from django.views import View
from ..Views.V_CommFunction import * 

class M_ItemTag(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                # print('ItemTag API StartTime: ',datetime.now())
                query = M_Items.objects.raw('''select id,Name, Tag from M_Items where Tag != '' ''')
                # return JsonResponse({'query':  str(query.query)})
                if not query:
                    log_entry = create_transaction_logNew(request, {'ItemTag':id}, 0, "Items Not available",100,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    # Items_Serializer = ItemSerializerSecond(query, many=True).data
                    ListData = list ()
                    for a in query:
                       
                        b=str(a.Tag)
                        c=b.split(',')
                        for d in c:
                            ListData.append({
                                "dta": d+ "-" + a.Name
                            })  
                    # print('ItemTag API EndTime: ',datetime.now())
                    log_entry = create_transaction_logNew(request, {'ItemTag':id}, 0,'',100,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ListData})         
        except Exception as e:
            # print('ItemTag API EndTime: ',datetime.now())
            log_entry = create_transaction_logNew(request,0, 0,'ItemTagList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
class MCUnitDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    def post(self, request):
        MaterialIssueIDdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ItemID = MaterialIssueIDdata['Item']   
                Itemsquery = MC_ItemUnits.objects.filter(Item=ItemID,IsDeleted=0)
                if Itemsquery.exists():
                    Itemsdata = ItemUnitsSerializerSecond(Itemsquery, many=True).data
                    UnitDetails=list()
                    for d in Itemsdata:  
                        UnitDetails.append({
                            "id": d['id'],
                            "UnitID": d['UnitID']['id'],
                            "UnitName": d['BaseUnitConversion'],
                            "BaseUnitQuantity": d['BaseUnitQuantity'],
                            "IsBase": d['IsBase'],
                            "PODefaultUnit": d['PODefaultUnit'],
                            "SODefaultUnit": d['SODefaultUnit'],         
                        })
                log_entry = create_transaction_logNew(request, MaterialIssueIDdata, 0, '',101,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UnitDetails})
        except Exception as e:
            log_entry = create_transaction_logNew(request, MaterialIssueIDdata, 0,'UnitDetails of Items:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})       
        
class M_ItemsFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request, id=0 ):
        Logindata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                # print("ItemFilterAPI StartTime : ",datetime.now())
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']
                PartyID=Logindata['PartyID'] 
                CompanyGroupID =Logindata['CompanyGroup'] 
                IsSCMCompany = Logindata['IsSCMCompany'] 
                IsBOM = Logindata['IsBOM'] 
                
                ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(PartyID,0).split('!')
                
                #for log
                if PartyID == '':
                        x = 0
                else:
                        x = PartyID
                
                if IsSCMCompany == 1:
                    
                    company_ids = C_Companies.objects.filter(CompanyGroup=CompanyGroupID).values_list('id', flat=True)
                    company_ids_tuple = tuple(company_ids)  
                    company_ids_str = ', '.join(map(str, company_ids_tuple))
                    
                    query= M_Items.objects.raw(f'''SELECT M_Items.id,M_Items.Name, M_Items.ShortName, M_Items.Sequence, M_Items.BarCode, M_Items.SAPItemCode,
                                               M_Items.isActive, M_Items.IsSCM, M_Items.CanBeSold, M_Items.CanBePurchase, M_Items.BrandName, M_Items.Tag,
                                               M_Items.CreatedBy, M_Items.CreatedOn, M_Items.UpdatedBy, M_Items.UpdatedOn, M_Items.Breadth, M_Items.Grammage,
                                               M_Items.Height, M_Items.Length, M_Items.StoringCondition, M_Items.BaseUnitID_id, M_Items.Company_id, 
                                               M_Items.Budget,C_Companies.Name AS CompanyName, M_Units.Name AS BaseUnitName,{ItemsGroupJoinsandOrderby[0]}
                                               FROM M_Items 
                                               JOIN M_Units ON M_Units.id=M_Items.BaseUnitID_id 
                                               JOIN C_Companies ON C_Companies.id = M_Items.Company_id 
                                               {ItemsGroupJoinsandOrderby[1]}
                                               WHERE M_Items.IsSCM=1 AND  M_Items.Company_id IN ({company_ids_str})
                                               {ItemsGroupJoinsandOrderby[2]}''') 
                    # CustomPrint(query.query)  
                else:
                    # query = M_Items.objects.select_related().filter(Company=CompanyID).order_by('Sequence')
                    query= M_Items.objects.raw(f'''SELECT M_Items.id,M_Items.Name, M_Items.ShortName, M_Items.Sequence, 
                                               M_Items.BarCode, M_Items.SAPItemCode, M_Items.isActive, M_Items.IsSCM,
                                               M_Items.CanBeSold, M_Items.CanBePurchase, M_Items.BrandName,
                                               M_Items.Tag, M_Items.CreatedBy, M_Items.CreatedOn, 
                                               M_Items.UpdatedBy, M_Items.UpdatedOn, M_Items.Breadth, 
                                               M_Items.Grammage, M_Items.Height, M_Items.Length, 
                                               M_Items.StoringCondition, M_Items.BaseUnitID_id, 
                                               M_Items.Company_id, M_Items.Budget,C_Companies.Name AS CompanyName,
                                               M_Units.Name AS BaseUnitName,{ItemsGroupJoinsandOrderby[0]}
                                               FROM M_Items 
                                               JOIN M_Units ON M_Units.id=M_Items.BaseUnitID_id 
                                               JOIN C_Companies ON C_Companies.id = M_Items.Company_id 
                                               {ItemsGroupJoinsandOrderby[1]}
                                               WHERE M_Items.Company_id=%s 
                                               {ItemsGroupJoinsandOrderby[2]}''',([CompanyID]))

                if not query:
                    log_entry = create_transaction_logNew(request, Logindata, x, "Items Not available",102,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = ItemSerializerThird(query, many=True).data
                    ItemListData = list ()
                    
                    for a in Items_Serializer:
                        
                        UnitDetails = [] 
                        if PartyID > 0:  

                            if IsBOM == 1:                          
                             UnitDetails = UnitDropdown(a['id'], PartyID, 0) 
                        

                        ItemListData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "ShortName": a['ShortName'],
                            "Company": a['Company_id'],
                            "CompanyName": a['CompanyName'],
                            "BaseUnitID": a['BaseUnitID_id'],
                            "BaseUnitName": a['BaseUnitName'],
                            "BarCode": a['BarCode'],
                            "Sequence": a['Sequence'],
                            "isActive":a['isActive'] ,
                            "IsSCM":a['IsSCM'] ,
                            "CanBeSold":a['CanBeSold'] ,
                            "CanBePurchase":a['CanBePurchase'],
                            "BrandName":a['BrandName'] ,
                            "Tag":a['Tag'],
                            "Length":a['Length'],
                            "Breadth":a['Breadth'],
                            "Height":a['Height'],
                            "StoringCondition":a['StoringCondition'],
                            "Grammage":a['Grammage'],
                            "Budget":a['Budget'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "UnitDetails":UnitDetails
                        }) 

                    # print("ItemFilterAPI EndTime : ",datetime.now())    
                    log_entry = create_transaction_logNew(request, Logindata, x,'Party Items List',102,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemListData})   
        except Exception as e:
            # print("ItemFilterAPI EndTime : ",datetime.now())
            log_entry = create_transaction_logNew(request, Logindata, 0,'ItemList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
#---- M_Items Save Class
class M_ItemsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,) 
    
    @transaction.atomic()
    def post(self, request):
        Itemsdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                # print("ItemSaveAPI StartTime : ",datetime.now())
                
                query = M_Units.objects.filter(id=Itemsdata['BaseUnitID']).values('Name')
                BaseUnitName = query[0]['Name']
                
                for a in Itemsdata['ItemUnitDetails']:
                    query2 = M_Units.objects.filter(id=a['UnitID']).values('Name')
                    ChildUnitName = query2[0]['Name']                    
                    # B = Decimal(a['BaseUnitQuantity']).normalize()
                    B=Decimal('{:f}'.format(Decimal(a['BaseUnitQuantity']).normalize()))
                    if a['IsBase'] == 0:
                        BaseUnitConversion=ChildUnitName+" ("+str(B)+" "+BaseUnitName+")"
                    else:
                        BaseUnitConversion=ChildUnitName    
                    a.update({"BaseUnitConversion":BaseUnitConversion})
                    
                Items_Serializer = ItemSerializer(data=Itemsdata)
                
                if Items_Serializer.is_valid():
                    Item = Items_Serializer.save()
                    LastInsertID = Item.id
                    
                    # print("ItemSaveAPI EndTime : ",datetime.now())
                    
                    log_entry = create_transaction_logNew(request, Itemsdata, 0,'TransactionID:'+str(LastInsertID),103,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Save Successfully','TransactionID':LastInsertID,'Data' :[]})
                
                else:
                    
                    # print("ItemSaveAPI EndTime : ",datetime.now())
                    log_entry = create_transaction_logNew(request, Itemsdata, 0,'ItemSave:'+str(Items_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': Items_Serializer.errors,'Data': []})
        
        except Exception as e:
            # print("ItemSaveAPI EndTime : ",datetime.now())
            log_entry = create_transaction_logNew(request, Itemsdata, 0,'ItemSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
# Get and Update M_Items
class M_ItemsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                
                # print("ItemSingleGETAPI StartTime : ",datetime.now())
                
                Itemsquery = M_Items.objects.filter(id=id)
                
                if Itemsquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Itemsdata = ItemSerializerSecond(Itemsquery, many=True).data
                    # return JsonResponse({'query':  Itemsdata})
                    ItemData=list()
                    for a in Itemsdata:
                        
                        CategoryDetails=list()
                        for b in a['ItemCategoryDetails']:
                            CategoryDetails.append({
                                "id": b['id'],
                                "CategoryType": b['CategoryType']['id'],
                                "CategoryTypeName": b['CategoryType']['Name'],
                                "Category": b['Category']['id'],
                                "CategoryName": b['Category']['Name'],
                            })
                        
                        GroupDetails=list()
                        for c in a['ItemGroupDetails']:
                            GroupDetails.append({
                                "id": c['id'],
                                "GroupType": c['GroupType']['id'],
                                "GroupTypeName": c['GroupType']['Name'],
                                "Group": c['Group']['id'],
                                "GroupName": c['Group']['Name'],
                                "SubGroup": c['SubGroup']['id'],
                                "SubGroupName": c['SubGroup']['Name'],
                            })
                        
                        UnitDetails=list()
                        for d in a['ItemUnitDetails']:
                            if d['IsDeleted']== 0 :
                                UnitDetails.append({
                                    "id": d['id'],
                                    "UnitID": d['UnitID']['id'],
                                    "UnitName": d['UnitID']['Name'],
                                    "BaseUnitQuantity": d['BaseUnitQuantity'],
                                    "IsBase": d['IsBase'],
                                    "PODefaultUnit": d['PODefaultUnit'],
                                    "SODefaultUnit": d['SODefaultUnit'],
                                    "IsShowUnit":d['IsShowUnit'] 
                                })
                            
                        # ImagesDetails=list()
                        # for e in a['ItemImagesDetails']:
                        #     ImagesDetails.append({
                        #         "id": e['id'],
                        #         "Item_pic": e['Item_pic'],
                        #         "ImageType": e['ImageType']['id'],
                        #         "ImageTypeName": e['ImageType']['Name'], 
                        #     })        
                        
                        DivisionDetails=list()
                        for f in a['ItemDivisionDetails']:
                            DivisionDetails.append({
                                "id": f['id'],
                                "Party": f['Party']['id'],
                                "PartyName": f['Party']['Name'], 
                            })    
                        
                        MRPDetails=list()
                        for g in a['ItemMRPDetails']:
                            if g['IsDeleted']== 0 :
                                MRPDetails.append({
                                    "id": g['id'],
                                    "EffectiveDate": g['EffectiveDate'],
                                    "Company": g['Company']['id'],
                                    "CompanyName": g['Company']['Name'],
                                    "MRP": g['MRP'],
                                    "Party": g['Party']['id'],
                                    "PartyName": g['Party']['Name'],
                                    "Division":g['Division']['id'],
                                    "DivisionName":g['Division']['Name'],
                                    "CreatedBy":g['CreatedBy'],
                                    "UpdatedBy":g['UpdatedBy'],
                                    "IsAdd":False
                                })
                        
                        MarginDetails=list()
                        for h in a['ItemMarginDetails']:
                            if h['IsDeleted']== 0 :
                                MarginDetails.append({
                                    "id": h['id'],
                                    "EffectiveDate": h['EffectiveDate'],
                                    "Company": h['Company']['id'],
                                    "CompanyName": h['Company']['Name'],
                                    "Party": h['Party']['id'],
                                    "PartyName": h['Party']['Name'],
                                    "Margin": h['Margin'],
                                    "CreatedBy":h['CreatedBy'],
                                    "UpdatedBy":h['UpdatedBy'],
                                    "PriceList":h['PriceList']['id'],
                                    "PriceListName":h['PriceList']['Name'],
                                    "IsAdd":False   
                                })
                        
                        GSTHSNDetails=list()
                        for i in a['ItemGSTHSNDetails']:
                            if i['IsDeleted']== 0 :
                                GSTHSNDetails.append({
                                    "id": i['id'],
                                    "EffectiveDate": i['EffectiveDate'],
                                    "GSTPercentage": i['GSTPercentage'],
                                    "HSNCode": i['HSNCode'],
                                    "Company": i['Company']['id'],
                                    "CompanyName": i['Company']['Name'],
                                    "CreatedBy":i['CreatedBy'],
                                    "UpdatedBy":i['UpdatedBy'],
                                    "IsAdd":False
                                })
                                
                        ShelfLifeDetails=list()
                        for j in a['ItemShelfLife']:
                            if j['IsDeleted']== 0 :
                                ShelfLifeDetails.append({
                                    "id": j['id'],
                                    "Days": j['Days'],
                                    "CreatedBy":j['CreatedBy'],
                                    "UpdatedBy":j['UpdatedBy'],
                                    "IsAdd":False
                                })
                        
                        bb=str(a['BrandName'])
                        if bb == '':
                            BrandName= list()   
                        else:     
                            BrandName= list()
                            cc=bb.split(',')
                            query = M_GeneralMaster.objects.filter(id__in=cc)
                            GeneralMaster_Serializer = GeneralMasterserializer(query, many=True).data
                            for k in GeneralMaster_Serializer:   
                                BrandName.append({
                                "id":k['id'],    
                                "Name": k['Name']   
                                })  
                             
                        ItemData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "ShortName": a['ShortName'],
                            "Company": a['Company']['id'],
                            "CompanyName": a['Company']['Name'],
                            "BaseUnitID": a['BaseUnitID']['id'],
                            "BaseUnitName": a['BaseUnitID']['Name'],
                            "BarCode": a['BarCode'],
                            "SAPItemCode":a['SAPItemCode'],
                            "Sequence": a['Sequence'],
                            "isActive":a['isActive'] ,
                            "IsSCM":a['IsSCM'] ,
                            "CanBeSold":a['CanBeSold'] ,
                            "CanBePurchase":a['CanBePurchase'],
                            "BrandName":BrandName,
                            "Tag":a['Tag'],
                            "Length":a['Length'],
                            "Breadth":a['Breadth'],
                            "Height":a['Height'],
                            "StoringCondition":a['StoringCondition'],
                            "Budget":a['Budget'],
                            "Grammage":a['Grammage'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "IsCBMItem": a['IsCBMItem'],
                            "IsMixItem":a['IsMixItem'],
                            "ItemCategoryDetails" : CategoryDetails,
                            "ItemGroupDetails" : GroupDetails,
                            "ItemUnitDetails": UnitDetails, 
                            # "ItemImagesDetails" : ImagesDetails,
                            "ItemDivisionDetails": DivisionDetails,
                            "ItemMRPDetails":MRPDetails,
                            "ItemMarginDetails":MarginDetails, 
                            "ItemGSTHSNDetails":GSTHSNDetails,
                            "ItemShelfLife":ShelfLifeDetails
                        })
                        
                    # print("ItemSingleGETAPI EndTime : ",datetime.now())
                    
                    log_entry = create_transaction_logNew(request, {'ItemID':id}, 0,'',181,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ItemData[0]})
                
                # print("ItemSingleGETAPI EndTime : ",datetime.now())
                
                log_entry = create_transaction_logNew(request, {'ItemID':id}, 0, "Items Not available",103,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
            
        except M_Items.DoesNotExist:
            
            # print("ItemSingleGETAPI EndTime : ",datetime.now())
            
            log_entry = create_transaction_logNew(request,0, 0, "Items Not available",181,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        
        except Exception as e:
            
            # print("ItemSingleGETAPI EndTime : ",datetime.now())
            log_entry = create_transaction_logNew(request,0, 0,'Item SingleGETmethod :'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
# update M_Items 
    @transaction.atomic()
    def put(self, request, id=0):
        M_Itemsdata = JSONParser().parse(request)
        try:
            with transaction.atomic(): 
                
                M_ItemsdataByID = M_Items.objects.get(id=id)
                query = M_Units.objects.filter(id=M_Itemsdata['BaseUnitID']).values('Name')
                BaseUnitName = query[0]['Name']
                
                for a in M_Itemsdata['ItemUnitDetails']:
                    query2 = M_Units.objects.filter(id=a['UnitID']).values('Name')
                    ChildUnitName = query2[0]['Name']
                    B=Decimal('{:f}'.format(Decimal(a['BaseUnitQuantity']).normalize()))
                    if a['IsBase'] == 0:
                        BaseUnitConversion=ChildUnitName+" ("+str(B)+" "+BaseUnitName+")"
                    else:
                        BaseUnitConversion=ChildUnitName    
                    a.update({"BaseUnitConversion":BaseUnitConversion})
                    # ItemSerializer
                    
                M_Items_Serializer = ItemSerializer(M_ItemsdataByID, data=M_Itemsdata) 
                
                if M_Items_Serializer.is_valid():
                    UpdatedItem = M_Items_Serializer.save()
                    LastInsertID = UpdatedItem.id
                    log_entry = create_transaction_logNew(request, M_Itemsdata, 0,'',104,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Updated Successfully','TransactionID':LastInsertID,'Data' : []})
                else:
                    log_entry = create_transaction_logNew(request, M_Itemsdata, 0,'ItemEdit:'+str(M_Items_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': M_Items_Serializer.errors,'Data' :[]})
                
        except Exception as e:
            log_entry = create_transaction_logNew(request, M_Itemsdata, 0,'ItemEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = M_Items.objects.get(id=id)
                M_Itemsdata.delete()
                log_entry = create_transaction_logNew(request, {'ItemID':id}, 0,'',105,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Deleted Successfully','TransactionID':id,'Data':[]})
        except M_Items.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0, 0,"Item Not available",105,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request, 0, 0,"Item used in another table",8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item used in another table', 'Data': []}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'ItemDelete:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class M_ImageTypesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                ImageTypesdata = M_ImageTypes.objects.all()
                if ImageTypesdata.exists():
                    ImageTypes_Serializer = ImageTypesSerializer(ImageTypesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ImageTypes_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'ImageTypes Not Available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

# class ProductAndMarginReportView(CreateAPIView):
#     permission_classes = (IsAuthenticated,)

#     @transaction.atomic()
#     def get(self, request,IsSCM=0,PartyID=0):
#         try:
#             with transaction.atomic():
#                 # CustomPrint(IsSCM)
#                 if IsSCM == '0':
#                     Itemsdata = M_Items.objects.all()
#                 else:
#                     partyitem=MC_PartyItems.objects.filter(Party=PartyID).values('Item')
#                     Itemsdata = M_Items.objects.filter(id__in=partyitem)
                
#                 # CustomPrint(Itemsdata.query)
#                 if Itemsdata.exists():
#                     Itemsdata_Serializer = ItemReportSerializer(Itemsdata,many=True).data
#                     ItemsList = list()
#                     for a in Itemsdata_Serializer:
                        
                       

#                         if a['Length'] is None:
#                             BoxSize=""
                            
#                         else:    
#                             BoxSize= a['Length']+" L X "+a['Breadth']+" B X "+a['Height']+" W - MM"
                        
#                         ItemMargindata = M_MarginMaster.objects.filter(Item=a['id'],IsDeleted=0).values('Margin').order_by('-EffectiveDate','-id')[:1]
#                         ItemMRPdata = M_MRPMaster.objects.filter(Item=a['id'],IsDeleted=0,Division_id__isnull=True,Party_id__isnull=True).values('MRP').order_by('-id')[:1]
#                         ItemGstHsnCodedata = M_GSTHSNCode.objects.filter(Item=a['id'],IsDeleted=0).values('GSTPercentage','HSNCode').order_by('-EffectiveDate','-id')[:1]
#                         Itemshelfdata = MC_ItemShelfLife.objects.filter(Item=a['id'],IsDeleted=0).values('Days').order_by('-id')[:1]
#                         PcsInBoxQuery = MC_ItemUnits.objects.filter(Item=a['id'],IsDeleted=0,UnitID=4).values('BaseUnitQuantity')
#                         PcsInKgQuery = MC_ItemUnits.objects.filter(Item=a['id'],IsDeleted=0,UnitID=2).values('BaseUnitQuantity')
#                         if PcsInBoxQuery :
#                             PcsInBox =float(PcsInBoxQuery[0]['BaseUnitQuantity'])
#                         else:
#                             PcsInBox = 0.00

#                         if PcsInKgQuery :
#                             PcsInKG =float(PcsInKgQuery[0]['BaseUnitQuantity'])
#                         else:
#                             PcsInKG = 0.00    
                        
#                         if ItemMRPdata.count() == 0:
#                             MRPV=0
#                         else:    
#                             MRPV=float(ItemMRPdata[0]['MRP'])
                        
#                         if IsSCM == '0' :
#                             query = M_PriceList.objects.values('id','Name')
#                         else:
#                             qur1=MC_PartySubParty.objects.filter(Q(Party=PartyID)|Q(SubParty=PartyID)).values('SubParty')
#                             qur2=M_Parties.objects.filter(id__in=qur1).values('PriceList').distinct()
#                             query = M_PriceList.objects.values('id','Name').filter(id__in=qur2)
                        
                        
                        
#                         ItemMargins=list()
#                         RateList=list()
                        
#                         for x in query:
                            
#                             Margin=MarginMaster(a['id'],x['id'],0,date.today()).GetTodaysDateMargin()
#                             Rate=RateCalculationFunction(0,a['id'],0,0,1,0,x['id']).RateWithGST()
                            
#                             string1 = x['Name']
#                             string2 = string1.replace(" ","")
#                             ItemMargins.append({
#                                 string2+'Margin' : str(float(Margin[0]['TodaysMargin'])) + '%'
                              
                                
#                             })
#                             RateList.append({
                               
#                                 string2+'RateWithGST' : float(Rate[0]['RatewithGST']),
#                                 string2+'RateWithOutGST' : float(Rate[0]['RateWithoutGST'])
#                             })
                        
#                         ww=ItemMargins+RateList
#                         # print(a['id'])
#                         ItemsList.append({

#                             "FE2ItemID": a['id'],
#                             "SAPCode":a['SAPItemCode'],
#                             "Barcode":a['BarCode'],
#                             "HSNCode":str(ItemGstHsnCodedata[0]['HSNCode']),
#                             "Company": a['Company']['Name'],
#                             "SKUActiveDeactivestatus":a['isActive'],
#                             "BoxSize":BoxSize,
#                             "StoringCondition":a['StoringCondition'],
#                             "Product":a['ItemGroupDetails'][0]['Group']['Name'],
#                             "subProduct":a['ItemGroupDetails'][0]['SubGroup']['Name'],
#                             "ItemName": a['Name'],
#                             "ItemShortName":a['ShortName'],
#                             "MRP":MRPV,
#                             "GST":str(float(ItemGstHsnCodedata[0]['GSTPercentage'])) + '%',
#                             "BaseUnit": a['BaseUnitID']['Name'],
#                             "SKUVol":a['Grammage'],
#                             "ShelfLife":float(Itemshelfdata[0]['Days']),
#                             "PcsInBox":PcsInBox,
#                             "PcsInKG":PcsInKG,
#                             "ItemMargins":ww
                            
#                         })
#                     log_entry = create_transaction_logNew(request, Itemsdata_Serializer, 0,'',106,0)
#                     return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemsList})
#                 log_entry = create_transaction_logNew(request,Itemsdata_Serializer, 0,"Report Not Available",106,0)
#                 return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Item Not Available', 'Data': []})    
#         except Exception as e:
#             log_entry = create_transaction_logNew(request, 0, 0,'ProductAndMarginReport:'+str(Exception(e)),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


# API For Item Master Bulk Update 
class ItemWiseUpdateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic() 
    def post(self, request, id=0):
        Item_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                Type = Item_data['Type']
                GroupTypeID = Item_data['GroupType']
                CompanyID= Item_data['CompanyID']
                
                query = M_Items.objects.raw(f'''SELECT  M_Items.id, M_Items.Name,M_Group.id GroupID,MC_SubGroup.id SubGroupID, MC_ItemShelfLife.Days AS ShelfLife,
                                                            M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName,M_Items.ShortName, M_Items.Sequence, M_Items.BarCode, M_Items.SAPItemCode, M_Items.Breadth, M_Items.Grammage, M_Items.Height,
                                                            M_Items.Length, M_Items.StoringCondition, M_Items.SAPUnitID,CASE WHEN M_Items.IsCBMItem=null THEN 0 WHEN M_Items.IsCBMItem=0 THEN false ELSE true END as IsCBMItem,
                                                            CASE WHEN M_Items.IsMixItem=null THEN 0 WHEN M_Items.IsMixItem=0 THEN false ELSE true END as IsMixItem
                                                            FROM M_Items
                                                            LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id  and  MC_ItemGroupDetails.GroupType_id= {GroupTypeID}
                                                            LEFT JOIN MC_ItemShelfLife ON M_Items.id = MC_ItemShelfLife.Item_id AND IsDeleted=0
                                                            LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                                                            LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id  Where  M_Items.Company_id={CompanyID}
                                                            ORDER BY M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence ''') 
                
                Item_Serializer = ItemWiseUpdateSerializer(query, many=True).data
                ItemListData = list() 
                
                for a in Item_Serializer:
                    ItemListData.append({
                                "id": a['id'],
                                "ItemName": a['Name'],
                                "GroupID": a['GroupID'],
                                "GroupName": a['GroupName'],
                                "SubGroupID": a['SubGroupID'],
                                "SubGroupName": a['SubGroupName'],
                                 Type: a.get(Type)
                         })
                log_entry = create_transaction_logNew(request, Item_data, 0,f'Type: {Type}',349,0)       
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemListData})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Item_data, 0,'ItemWiseBulkUpdate:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

class ItemWiseSaveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        Item_data  = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ItemType = Item_data ['Type']
                Updated_data = Item_data ['UpdatedData']
                Created_By = request.user.id 
                
                for a in Updated_data:
                    ItemID = a.get('ItemID')
                    
                    if ItemID is None:
                        return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'ItemID is required', 'Data': []})
                    
                    if ItemType == 'ShelfLife':
                        ShelfLifeDays = a.get('Value1')
                        query1 = MC_ItemShelfLife.objects.filter(Item_id=ItemID).first()
                        if query1:
                            query1.Days = ShelfLifeDays
                            query1.save()
                        else:
                            MC_ItemShelfLife.objects.create(Item_id=ItemID, Days=ShelfLifeDays, CreatedBy=Created_By, UpdatedBy=Created_By) 

                    elif ItemType == 'Group':   
                        GroupID = a.get('Value1')
                        SubGroupID = a.get('Value2')
                        GroupTypeID = a.get('GroupTypeID')  
                        query2 = MC_ItemGroupDetails.objects.filter(Item_id=ItemID).first()
                        if query2:
                            query2.Group_id = GroupID
                            query2.SubGroup_id = SubGroupID
                            query2.GroupType_id = GroupTypeID  
                            query2.save()
                        else:
                            MC_ItemGroupDetails.objects.create(Item_id=ItemID, Group_id=GroupID, SubGroup_id=SubGroupID, GroupType_id=GroupTypeID)  
                    
                    else:
                        M_Items.objects.filter(id=ItemID).update(**{ItemType: a.get('Value1')})  
                        
                log_entry = create_transaction_logNew(request, Item_data, 0, f'Type: {ItemType} ItemID: {ItemID}', 350, 0)       
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': f'{ItemType} Updated Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Item_data, 0,'ItemDataSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 500, 'Status': True, 'Message': Exception(e), 'Data': []})
        

class ImageUploadsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser,MultiPartParser,FormParser]

    @transaction.atomic() 
    def post(self, request):
        try:
            with transaction.atomic():
               
                ItemImage_data = {
                    "Item" : request.POST.get('Item'),
                    "ImageType" : request.POST.get('ImageType')
                } 

                Imagequery = MC_ItemImages.objects.filter(Item=request.POST.get('Item'), ImageType=request.POST.get('ImageType'))
                Imagequery.delete()
                '''Image Upload Code start''' 
                avatar = request.FILES.getlist('Item_pic')
                for file in avatar:
                    ItemImage_data['Item_pic']=file
                '''Image Upload Code End'''
                ItemImages_Serializer = ItemImagesSerializer(
                    data=ItemImage_data)
                if ItemImages_Serializer.is_valid():
                    ItemImages_Serializer.save()
                    log_entry = create_transaction_logNew(request,ItemImage_data, 0,'',264,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Images Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,ItemImage_data, 0,'ImageUploadMethod:'+str(ItemImages_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  ItemImages_Serializer.errors, 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'ImageUploadMethod:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []}) 

    
    
    @transaction.atomic()
    def get(self, request,ItemID=0):
        try:
            with transaction.atomic():
                ItemImagequery = MC_ItemImages.objects.filter(Item_id=ItemID)
                   
                ItemImagedata = ItemImagesSerializer(ItemImagequery, many=True).data
                log_entry = create_transaction_logNew(request,ItemImagedata, 0,'',265,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ItemImagedata})
            log_entry = create_transaction_logNew(request,ItemImagedata, 0,'Group Not available',265,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'GroupGETMethod'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data':[]})        


class MC_ItemUnitsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request):
        try:
            with transaction.atomic():
                query = MC_ItemUnits.objects.raw('''Select MC_ItemUnits.id, BaseUnitQuantity,IsDeleted, IsBase, PODefaultUnit, SODefaultUnit, BaseUnitConversion, Item_id ItemID, UnitID_id Unit_ID, M_Units.Name UnitName
                                                From MC_ItemUnits
                                                Join M_Units on MC_ItemUnits.UnitID_id = M_Units.id where IsDeleted=0 order by Item_id ''')
                if query:
                    ItemUnitsMA_serializer = ItemUnitsForMobileAppSerializer(query, many=True).data
                    ItemUnitList = list()
                    for a in ItemUnitsMA_serializer:
                        ItemUnitList.append({
                            "id" : a["id"],
                            "BaseUnitQuantity":a['BaseUnitQuantity'],
                            "IsDeleted":a['IsDeleted'],
                            "IsBase":a['IsBase'],
                            "PODefaultUnit":a['PODefaultUnit'],
                            "SODefaultUnit":a['SODefaultUnit'],
                            "BaseUnitConversion":a['BaseUnitConversion'],
                            "Item":a['ItemID'],
                            "UnitID":a['Unit_ID'],
                            "UnitName":a['UnitName']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :ItemUnitList})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Unit not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]}) 