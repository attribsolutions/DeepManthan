from decimal import Decimal
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

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
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ListData})         
        except Exception as e:
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
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UnitDetails})
        except Exception as e:
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
                
                if IsSCMCompany == 1:
                    Company=C_Companies.objects.filter(CompanyGroup=CompanyGroupID)
                    query = M_Items.objects.filter(IsSCM=1,Company__in=Company).order_by('Sequence')
                else:
                    query = M_Items.objects.filter(Company=CompanyID).order_by('Sequence')
                # return JsonResponse({'query':  str(query.query)})
                if not query:
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
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "UnitDetails":UnitDetails
                        })    
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ItemListData})   
        except Exception as e:
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
                    Items_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Save Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': Items_Serializer.errors,'Data': []})
        except Exception as e:
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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ItemData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': M_Items_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = M_Items.objects.get(id=id)
                M_Itemsdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Deleted Successfully','Data':[]})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Item used in another table', 'Data': []}) 
        except Exception as e:
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
