from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from rest_framework.parsers import JSONParser
from ..Serializer.S_CentralServiceItemMaster import *
from ..models import *
from ..Serializer.S_Items import *
from ..Serializer.S_GRNs import *


class CentralServiceItemView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                ServiceItem_data = M_CentralServiceItems.objects.all()
                ServiceItem_Serializer = CentralServiceItemSerializer(ServiceItem_data,many=True)
                log_entry = create_transaction_logNew(request, ServiceItem_Serializer,0,'',273,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': ServiceItem_Serializer.data})
        except  M_CentralServiceItems.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Central service item save Data Not available',273,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Central service item save Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GETAllServiceItems:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
   
    def post(self, request):
        ServiceItem_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ServiceItem_Serializer = CentralServiceItemSerializer(data=ServiceItem_data)
                if ServiceItem_Serializer.is_valid():
                    ServiceItem_Serializer.save()
                    log_entry = create_transaction_logNew(request, ServiceItem_data,0,'',274,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Central service item save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, ServiceItem_data,0,'CentralServiceItemSave:'+str(ServiceItem_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  ServiceItem_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ServiceItem_data,0,'CentralServiceItemSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
class CentralServiceItemViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ServiceItem_data = M_CentralServiceItems.objects.filter(id=id)
                ServiceItem_Serializer = CentralServiceItemGetSerializer(ServiceItem_data,many=True).data
                ServiceItemList = list()
                for a in ServiceItem_Serializer:
                    ServiceItemList.append({
                        "id": a["id"],
                        "Name": a['Name'],
                        "HSNCode": a['HSNCode'], 
                        "GSTPercentage": a['GSTPercentage'], 
                        "isActive": a['isActive'],
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "UpdatedBy": a['UpdatedBy'],
                        "UpdatedOn": a['UpdatedOn'],
                        "Rate":a['Rate'],
                        "Unit": a['Unit']['id'],
                        "UnitName": a['Unit']['Name'],
                        "Company":a['Company'],
                        
                    })
                log_entry = create_transaction_logNew(request, ServiceItem_Serializer,0,'',275,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': ServiceItemList[0]})
        except  M_CentralServiceItems.DoesNotExist:
            log_entry = create_transaction_logNew(request, ServiceItem_Serializer,0,'',275,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Central Service Item Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GETSingleServiceItem:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
    @transaction.atomic()
    def put(self, request, id=0):
        ServiceItem_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ServiceItem_SerializerByID = M_CentralServiceItems.objects.get(id=id)
                ServiceItem_serializer = CentralServiceItemSerializer(ServiceItem_SerializerByID, data=ServiceItem_data)
                if ServiceItem_serializer.is_valid():
                    ServiceItem_serializer.save()
                    log_entry = create_transaction_logNew(request, ServiceItem_data,0,'',276,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Central Service Item Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, ServiceItem_data,0,'CentralServiceItemUpdated:'+str(ServiceItem_serializer.errors),276,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ServiceItem_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ServiceItem_data,0,'CentralServiceItemUpdated:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})   
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = M_CentralServiceItems.objects.get(id=id)
                Cluster_data.delete()
                log_entry = create_transaction_logNew(request, {'ClusterID':id},0,'ClusterID:'+str(id),277,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Central Service Item Data Deleted Successfully','Data':[]})
        except M_CentralServiceItems.DoesNotExist:
            log_entry = create_transaction_logNew(request, {'ClusterID':id},0,'ClusterID:'+str(id),277,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Central Service Item Data Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request, {'ClusterID':id},0,'ClusterID:'+str(id),8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Central Service Item Data used in another table', 'Data': []})
                
                
class CentralServiceItemAssignFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
 

    @transaction.atomic()
    def post(self, request):
        ServiceItemdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyID=ServiceItemdata['PartyID'] 
                CompanyID=ServiceItemdata['CompanyID']
                ServiceItemquery= MC_CentralServiceItemAssign.objects.raw('''SELECT distinct M_CentralServiceItems.id,M_CentralServiceItems.Name,ifnull(MC_CentralServiceItemAssign.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,(CASE WHEN MC_CentralServiceItemAssign.Rate IS NOT NULL AND MC_CentralServiceItemAssign.Rate <> 0 THEN MC_CentralServiceItemAssign.Rate ELSE M_CentralServiceItems.Rate END )AS Rate FROM M_CentralServiceItems LEFT JOIN MC_CentralServiceItemAssign ON MC_CentralServiceItemAssign.CentralServiceItem_id=M_CentralServiceItems.id AND MC_CentralServiceItemAssign.Party_id=%s LEFT JOIN M_Parties ON M_Parties.id=MC_CentralServiceItemAssign.Party_id where M_CentralServiceItems.Company_id =%s''',([PartyID],[CompanyID]))
                if not ServiceItemquery:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Central Service Items Not available', 'Data': []})
                else:
                    ServiceItems_Serializer = MC_CentralServiceItemAssignSerializer(ServiceItemquery, many=True).data
                    ServiceItemList = list()
                    for a in ServiceItems_Serializer:
                        ServiceItemList.append({
                            "ServiceItem": a['id'],
                            "ServiceItemName": a['Name'],
                            "Party": a['Party_id'], 
                            "PartyName": a['PartyName'],
                            "Rate":a['Rate']
                        })
                    log_entry = create_transaction_logNew(request, ServiceItemdata,PartyID,'',278,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ServiceItemList})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ServiceItemdata,0,'ListOfCentralServiceItemAssign:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})  
        
        
class CentralServiceItemAssignForParty(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        PartyItems_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyItems_serializer = MC_CentralServiceItemAssignSerializerSecond(data=PartyItems_data, many=True)
                if PartyItems_serializer.is_valid():
                    id = PartyItems_serializer.data[0]['Party']
                    ServiceItemParty_data = MC_CentralServiceItemAssign.objects.filter(Party=id)
                    ServiceItemParty_data.delete()
                    ServiceItem = PartyItems_serializer.save()
                    log_entry = create_transaction_logNew(request, PartyItems_data,id,'',279,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CentralServiceItem For Party Save Successfully', 'Data': []})
                log_entry = create_transaction_logNew(request, PartyItems_data,0,'CentralServiceItemAssignSave:'+str(PartyItems_serializer.errors),34,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PartyItems_serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartyItems_data, 0,'CentralServiceItemAssignSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})        
        

class CentralServiceItemViewThird(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        PurchaseReturndata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ItemID = PurchaseReturndata['ItemID']
                BatchCode = PurchaseReturndata['BatchCode']
                CustomerID =PurchaseReturndata['Customer']
                
                Itemquery = M_CentralServiceItems.objects.filter(id=ItemID)
                CentralServiceItems = list()
                if Itemquery:
                    GRNItemsdata = CentralServiceItemSerializer(Itemquery, many=True).data
                    for a in GRNItemsdata:
                        GSTPercentage= a['GSTPercentage']
                
                    ItemMRPDetails = list() 
                    ItemMRPDetails.append({
                                    "MRP":"",
                                    "MRPValue": "",
                                    "Rate" : a['Rate'],
                                }) 

                    ItemGSTDetails = list()
                        
                    ItemGSTDetails.append({
                            "GST": "",
                            "GSTPercentage":GSTPercentage,   
                        }) 

                    StockDatalist = list()
                        
                    StockDatalist.append({
                                "id": "",
                                "Item":"",
                                "BatchDate":"",
                                "BatchCode":"",
                                "SystemBatchDate":"",
                                "SystemBatchCode":"",
                                "LiveBatche" : "",
                                "LiveBatcheMRPID" : "",
                                "LiveBatcheGSTID" :"",
                                "Rate":"",
                                "MRP" : "",
                                "GST" : "",
                                "BaseUnitQuantity":"",
                                })

                    
                    CentralServiceItems.append({
                        "Item": a['id'],
                        "ItemName": a['Name'],
                        "MRP": "",
                        "MRPValue": "",
                        "Rate": a['Rate'],
                        "GST": "",
                        "GSTPercentage": GSTPercentage,
                        "BatchCode": "",
                        "BatchDate": "",
                        "Unit" :a['Unit'],
                        "UnitName" : "No", 
                        "ItemMRPDetails":ItemMRPDetails,
                        "ItemGSTDetails":ItemGSTDetails,
                        "StockDetails":StockDatalist 
                })   
                    # log_entry = create_transaction_logNew(request, PurchaseReturndata,0,'',280,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CentralServiceItems})
                # log_entry = create_transaction_logNew(request, PurchaseReturndata,0,'',280,0)
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request,PurchaseReturndata,0,'CentralServiceItem:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})      

