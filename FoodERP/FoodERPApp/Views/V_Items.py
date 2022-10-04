from genericpath import exists
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from  ..Serializer.S_Items import *
from ..models import *

 
class M_ItemsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_Items.objects.raw('''SELECT m_items.id,m_items.Name,m_items.ShortName,m_units.Name BaseUnitName,c_companies.Name CompanyName,m_items.BarCode  FROM m_items join m_units on m_units.id= m_items.BaseUnitID_id join c_companies on c_companies.id= m_items.Company_id Order BY m_items.Sequence''')
                # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': str(query.query)})
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = ItemsSerializerList(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Items_Serializer})   
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data':[]})
        
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Itemsdata = JSONParser().parse(request)
                Items_Serializer = ItemSerializer(data=Itemsdata)
                if Items_Serializer.is_valid():
                    Items_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Save Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': Items_Serializer.errors,'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' Exception Found', 'Data':[]})
        
    
 

class M_ItemsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Itemsquery = M_Items.objects.filter(id=id)
                if Itemsquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Itemsdata = ItemSerializerSecond(Itemsquery, many=True).data
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
                            UnitDetails.append({
                                "id": d['id'],
                                "UnitID": d['UnitID']['id'],
                                "UnitName": d['UnitID']['Name'],
                                "BaseUnitQuantity": d['BaseUnitQuantity'],
                            
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
                                "Division": f['Division']['id'],
                                "DivisionName": f['Division']['Name'],
                                
                            })    
                        
                        MRPDetails=list()
                        for g in a['ItemMRPDetails']:
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
                                "UpdatedBy":g['UpdatedBy']
                            })
                        
                        MarginDetails=list()
                        for h in a['ItemMarginDetails']:
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
                                   
                            })
                        
                        GSTHSNDetails=list()
                        for i in a['ItemGSTHSNDetails']:
                            GSTHSNDetails.append({
                                "id": i['id'],
                                "EffectiveDate": i['EffectiveDate'],
                                "GSTPercentage": i['GSTPercentage'],
                                "HSNCode": i['HSNCode'],
                                "CreatedBy":i['CreatedBy'],
                                "UpdatedBy":i['UpdatedBy']
                                
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
                            "Sequence": a['Sequence'],
                            "isActive":a['isActive'] ,
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
                            "ItemGSTHSNDetails":GSTHSNDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ItemData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
   
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Itemsdata = JSONParser().parse(request)
                M_ItemsdataByID = M_Items.objects.get(id=id)
                M_Items_Serializer = ItemSerializer(
                    M_ItemsdataByID, data=M_Itemsdata)
                if M_Items_Serializer.is_valid():
                    M_Items_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Item Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': M_Items_Serializer.errors,'Data' :[]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' Exception Found','Data' :[]})

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


class M_ImageTypesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
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

          