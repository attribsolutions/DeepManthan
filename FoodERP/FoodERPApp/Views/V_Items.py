from decimal import Decimal
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_PriceLists import *
from  ..Serializer.S_Items import *
from  ..Serializer.S_GeneralMaster import *
from ..models import *




class M_ItemTag(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Items.objects.all()
                # return JsonResponse({'query':  str(query.query)})
                if not query:
                    log_entry = create_transaction_log(request, {'ItemTag':id}, 0, 0, "Data Not available",7,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = ItemSerializerSecond(query, many=True).data
                    ListData = list ()
                    for a in Items_Serializer:
                        b=str(a['Tag'])
                        c=b.split(',')
                        for d in c:
                            ListData.append({
                                "dta": d+ "-" + a['Name']
                            })  
                    log_entry = create_transaction_log(request, {'ItemTag':id}, 0, 0, "Item Tag List",100,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ListData})         
        except Exception as e:
            log_entry = create_transaction_log(request, {'ItemTag':id}, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
class MCUnitDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIssueIDdata = JSONParser().parse(request)
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
                log_entry = create_transaction_log(request, {'ItemID':ItemID}, 0, 0, "UnitDetails",101,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UnitDetails})
        except Exception as e:
            log_entry = create_transaction_log(request, {'ItemID':ItemID}, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})       
        
class M_ItemsFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request, id=0 ):
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']
                PartyID=Logindata['PartyID'] 
                CompanyGroupID =Logindata['CompanyGroup'] 
                IsSCMCompany = Logindata['IsSCMCompany'] 
                
                if PartyID == '':
                        x = CompanyID
                else:
                        x = PartyID

                if IsSCMCompany == 1:
                    Company=C_Companies.objects.filter(CompanyGroup=CompanyGroupID)
                    query = M_Items.objects.select_related().filter(IsSCM=1,Company__in=Company).order_by('Sequence')
                else:
                    query = M_Items.objects.select_related().filter(Company=CompanyID).order_by('Sequence')
                # return JsonResponse({'query':  str(query.query)})
                if not query:
                    log_entry = create_transaction_log(request, Logindata, 0, x, "Data Not available",7,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = ItemSerializerSecond(query, many=True).data
                    ItemListData = list ()
                    for a in Items_Serializer:
                        UnitDetails=list()
                        for d in a['ItemUnitDetails']:
                            if d['IsDeleted']== 0 :
                                
                                UnitDetails.append({
                                    "id": d['id'],
                                    "UnitID": d['UnitID']['id'],
                                    "UnitName": d['BaseUnitConversion'],
                                    "BaseUnitQuantity": d['BaseUnitQuantity'],
                                    "IsBase": d['IsBase'],
                                    "PODefaultUnit": d['PODefaultUnit'],
                                    "SODefaultUnit": d['SODefaultUnit'],
                                })
                        ItemListData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "ShortName": a['ShortName'],
                            "Company": a['Company']['id'],
                            "CompanyName": a['Company']['Name'],
                            "BaseUnitID": a['BaseUnitID']['id'],
                            "BaseUnitName": a['BaseUnitID']['Name'],
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
                        
                    log_entry = create_transaction_log(request, Logindata, 0, x, "Item Filter List",102,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemListData})   
        except Exception as e:
            log_entry = create_transaction_log(request, Logindata, 0, x, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

class M_ItemsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Itemsdata = JSONParser().parse(request)
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
                    log_entry = create_transaction_log(request, Itemsdata, 0, 0, "Item Save Successfully",103,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Save Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_log(request, Itemsdata, 0, 0, Items_Serializer.errors,34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': Items_Serializer.errors,'Data': []})
        except Exception as e:
            log_entry = create_transaction_log(request, Itemsdata, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

class M_ItemsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
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
                                
                                })
                            
                        ImagesDetails=list()
                        for e in a['ItemImagesDetails']:
                            ImagesDetails.append({
                                "id": e['id'],
                                "Item_pic": e['Item_pic'],
                                "ImageType": e['ImageType']['id'],
                                "ImageTypeName": e['ImageType']['Name'],
                                
                            })        
                        
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
                            "ItemCategoryDetails" : CategoryDetails,
                            "ItemGroupDetails" : GroupDetails,
                            "ItemUnitDetails": UnitDetails, 
                            "ItemImagesDetails" : ImagesDetails,
                            "ItemDivisionDetails": DivisionDetails,
                            "ItemMRPDetails":MRPDetails,
                            "ItemMarginDetails":MarginDetails, 
                            "ItemGSTHSNDetails":GSTHSNDetails,
                            "ItemShelfLife":ShelfLifeDetails
                        })
                    log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0, "Item List",103,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ItemData[0]})
                log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0, "Data Not available",7,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0, "Data Not available",7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = JSONParser().parse(request)
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
                M_Items_Serializer = ItemSerializer(
                    M_ItemsdataByID, data=M_Itemsdata)
                if M_Items_Serializer.is_valid():
                    M_Items_Serializer.save()
                    log_entry = create_transaction_log(request, M_Itemsdata, 0, 0, "Item Updated Successfully",104,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Updated Successfully','Data' : []})
                else:
                    log_entry = create_transaction_log(request, M_Itemsdata, 0, 0,M_Items_Serializer.errors,34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': M_Items_Serializer.errors,'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_log(request, M_Itemsdata, 0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = M_Items.objects.get(id=id)
                M_Itemsdata.delete()
                log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0,"Item Deleted Successfully",105,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Deleted Successfully','Data':[]})
        except M_Items.DoesNotExist:
            log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0,"Data Not available",7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0,"Item used in another table'",8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item used in another table', 'Data': []}) 
        except Exception as e:
            log_entry = create_transaction_log(request, {'ItemID':id}, 0, 0,Exception(e),33,0)
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

class ProductAndMarginReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request,IsSCM=0,PartyID=0):
        try:
            with transaction.atomic():
                # print(IsSCM)
                if IsSCM == '0':
                    Itemsdata = M_Items.objects.all()
                else:
                    partyitem=MC_PartyItems.objects.filter(Party=PartyID).values('Item')
                    Itemsdata = M_Items.objects.filter(id__in=partyitem)
                
                # print(Itemsdata.query)
                if Itemsdata.exists():
                    Itemsdata_Serializer = ItemReportSerializer(Itemsdata,many=True).data
                    ItemsList = list()
                    for a in Itemsdata_Serializer:
                        
                       

                        if a['Length'] is None:
                            BoxSize=""
                            
                        else:    
                            BoxSize= a['Length']+" L X "+a['Breadth']+" B X "+a['Height']+" W - MM"
                        
                        ItemMargindata = M_MarginMaster.objects.filter(Item=a['id'],IsDeleted=0).values('Margin').order_by('-EffectiveDate','-id')[:1]
                        ItemMRPdata = M_MRPMaster.objects.filter(Item=a['id'],IsDeleted=0,Division_id__isnull=True,Party_id__isnull=True).values('MRP').order_by('-id')[:1]
                        ItemGstHsnCodedata = M_GSTHSNCode.objects.filter(Item=a['id'],IsDeleted=0).values('GSTPercentage','HSNCode').order_by('-EffectiveDate','-id')[:1]
                        Itemshelfdata = MC_ItemShelfLife.objects.filter(Item=a['id'],IsDeleted=0).values('Days').order_by('-id')[:1]

                        if ItemMRPdata.count() == 0:
                            MRPV=0
                        else:    
                            MRPV=float(ItemMRPdata[0]['MRP'])
                        
                        if IsSCM == '0' :
                            query = M_PriceList.objects.values('id','Name')
                        else:
                            qur1=MC_PartySubParty.objects.filter(Q(Party=PartyID)|Q(SubParty=PartyID)).values('SubParty')
                            qur2=M_Parties.objects.filter(id__in=qur1).values('PriceList').distinct()
                            query = M_PriceList.objects.values('id','Name').filter(id__in=qur2)
                        
                        
                        
                        ItemMargins=list()
                        RateList=list()
                        
                        for x in query:
                            
                            Margin=MarginMaster(a['id'],x['id'],0,date.today()).GetTodaysDateMargin()
                            Rate=RateCalculationFunction(0,a['id'],0,0,1,0,x['id']).RateWithGST()
                            
                            ItemMargins.append({
                                x['Name']+'Margin' : float(Margin[0]['TodaysMargin']),
                                
                            })
                            RateList.append({
                               
                                x['Name']+'RateWithGST' : float(Rate[0]['RatewithGST']),
                                x['Name']+'RateWithOutGST' : float(Rate[0]['RateWithoutGST'])
                            })
                        
                        ww=ItemMargins+RateList
                        print(a['id'])
                        ItemsList.append({

                            "FE2ItemID": a['id'],
                            "SAPCode":a['SAPItemCode'],
                            "Barcode":a['BarCode'],
                            "HSNCode":ItemGstHsnCodedata[0]['HSNCode'],
                            "ItemName": a['Name'],
                            "ItemShortName":a['ShortName'],
                            "SKUActiveDeactivestatus":a['isActive'],
                            "BoxSize":BoxSize,
                            "StoringCondition":a['StoringCondition'],
                            "MRP":MRPV,
                            "GST":float(ItemGstHsnCodedata[0]['GSTPercentage']),
                            "BaseUnit": a['BaseUnitID']['Name'],
                            "SKUGr":a['Grammage'],
                            "Product":a['ItemGroupDetails'][0]['Group']['Name'],
                            "subProduct":a['ItemGroupDetails'][0]['SubGroup']['Name'],
                            "Company": a['Company']['Name'],
                            "ShelfLife":float(Itemshelfdata[0]['Days']),
                            "ItemMargins":ww
                            
                        })
                    log_entry = create_transaction_log(request, {'ItemDetails':Itemsdata_Serializer}, 0, 0,"ProductAndMarginReport",106,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemsList})
                log_entry = create_transaction_log(request, {'ItemDetails':Itemsdata_Serializer}, 0, 0,"Data Not Available",7,0)
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Item Not Available', 'Data': []})    
        except Exception as e:
            log_entry = create_transaction_log(request, {'ItemDetails':Itemsdata_Serializer}, 0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


# class DiscountMasterSaveView(CreateAPIView):

#     permission_classes = (IsAuthenticated,)
#     # authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def post(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 DiscountMaster_data = JSONParser().parse(request)
#                 Discount_serializer = DiscountSerializer(data=DiscountMaster_data, many=True)
#                 if Discount_serializer.is_valid():
#                     Discount_serializer.save()
                
#                     log_entry = create_transaction_log(request, DiscountMaster_data, 0, 0,"Discount Master Save Successfully",107,0)
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Discount Master Save Successfully', 'Data': []})
#                 else:
#                     log_entry = create_transaction_log(request,DiscountMaster_data, 0, 0,Discount_serializer.errors,34,0)
#                     transaction.set_rollback(True)
#                     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Discount_serializer.errors, 'Data': []})
#         except Exception as e:
#             log_entry = create_transaction_log(request,DiscountMaster_data, 0, 0,Exception(e),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


# class DiscountMasterView(CreateAPIView):

#     permission_classes = (IsAuthenticated,)
#     # authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def get(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 DiscountMasterdata = M_DiscountMaster.objects.get(id=id)
#                 Discount_Serializer = DiscountSerializer(DiscountMasterdata)
#                 log_entry = create_transaction_log(request, {'DiscountMasterID':id}, 0, 0,"DiscountMaster",107,0)
#                 return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Discount_Serializer.data})
#         except  M_Bank.DoesNotExist:
#             log_entry = create_transaction_log(request, {'DiscountMasterID':id}, 0, 0,"Data Not available",33,0)
#             return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'DiscountMaster Not available', 'Data': []})
#         except Exception as e:
#             log_entry = create_transaction_log(request,{'DiscountMasterID':id}, 0, 0,Exception(e),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

#     @transaction.atomic()
#     def put(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 DiscountMasterdata = JSONParser().parse(request)
#                 DiscountMasterByID = M_DiscountMaster.objects.get(id=id)
#                 Discount_Serializer = DiscountSerializer(
#                     DiscountMasterByID, data=DiscountMasterdata)
#                 if Discount_Serializer.is_valid():
#                     Discount_Serializer.save()
#                     log_entry = create_transaction_log(request,DiscountMasterdata, 0, 0,"DiscountMaster Updated Successfully",109,id)
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'DiscountMaster Updated Successfully','Data' :[]})
#                 else:
#                     log_entry = create_transaction_log(request,DiscountMasterdata, 0, 0,Discount_Serializer.errors,34,0)
#                     transaction.set_rollback(True)
#                     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Discount_Serializer.errors, 'Data' :[]})
#         except Exception as e:
#             log_entry = create_transaction_log(request,DiscountMasterdata, 0, 0,Exception(e),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    

#     @transaction.atomic()
#     def delete(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 DiscountMasterdata = M_DiscountMaster.objects.get(id=id)
#                 DiscountMasterdata.delete()
#                 log_entry = create_transaction_log(request,{'DiscountMasterID':id}, 0, 0,"DiscountMaster Deleted Successfully",110,0)
#                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'DiscountMaster Deleted Successfully','Data':[]})
#         except M_Bank.DoesNotExist:
#             log_entry = create_transaction_log(request,{'DiscountMasterID':id}, 0, 0,"Data Not available",7,0)
#             return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'DiscountMaster Not available', 'Data': []})
#         except IntegrityError:
#             log_entry = create_transaction_log(request,{'DiscountMasterID':id}, 0, 0,"Bank used in transaction",8,0)
#             return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Bank used in transaction', 'Data': []})


# class GetDiscountView(CreateAPIView):
#     permission_classes = (IsAuthenticated,)
    
#     @transaction.atomic()
#     def post(self, request,id=0):
#         try:
#             with transaction.atomic():
#                 Discountdata = JSONParser().parse(request)
#                 FromDate = Discountdata['FromDate']
#                 ToDate = Discountdata['ToDate']
#                 PartyType = Discountdata['PartyType']
#                 PriceList = Discountdata['PriceList']
#                 Party = Discountdata['PartyID']
#                 Customer = Discountdata['CustomerID']

#                 if Party == '':
#                     x = Customer
#                 else:
#                     x = Party

#                 query = M_DiscountMaster.objects.filter(FromDate__range=[FromDate,ToDate],PartyType=PartyType,PriceList=PriceList)
#                 if query:
#                     Discount_Serializer = DiscountSerializerSecond(query, many=True).data
#                     DiscountList = list()
#                     for a in Discount_Serializer:
                        
#                         DiscountList.append({
#                             "ItemId":a['Item']['id'],
#                             "ItemName": a['Item']['Name'],
#                             "Discount":a['Discount'],
#                             "DiscountType":a['DiscountType']
                                 
#                         })
#                     log_entry = create_transaction_log(request,Discountdata, 0, x,"GetDiscount",111,0)
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':DiscountList})
#         except Exception as e:
#             log_entry = create_transaction_log(request,Discountdata, 0, x,Exception(e),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})






















# class GetDiscountView(CreateAPIView):

#     permission_classes = (IsAuthenticated,)
#     # authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def post(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 DiscountMaster_data = JSONParser().parse(request)
#                 FromDate=DiscountMaster_data['FromDate']
#                 ToDate=DiscountMaster_data['ToDate']
#                 PartyType=DiscountMaster_data['PartyType']
#                 PriceList=DiscountMaster_data['PriceList']
#                 PartyID=DiscountMaster_data['PartyID']
#                 # CustomerID=DiscountMaster_data['CustomerID'] 
#                 query = M_DiscountMaster.objects.all()

#                 if query:
#                     Discount_Serializer = DiscountSerializerSecond(query, many=True).data
#                     DiscountList = list()

#                     for a in Discount_Serializer:
#                         DiscountList.append({
#                             "ItemId":a['Item']['id'],
#                             "ItemName": a['Item']['Name'],
#                             "Discount":a['Discount'],
#                             "DiscountType":a['DiscountType']

#                         })
#                         return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':DiscountList})
#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

                   

            