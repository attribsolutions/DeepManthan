

from ..models import *
from ..Serializer.S_MappingMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *


class PartyCustomerMappingView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request):
        PartyCustomerMappingMaster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyCustomerMapping_Serializer = PartyMasterMappingSerializer(data=PartyCustomerMappingMaster_data,many=True)
                if PartyCustomerMapping_Serializer.is_valid():
                    id = PartyCustomerMapping_Serializer.data[0]['Party']
                    
                    Partycustomerdata = M_PartyCustomerMappingMaster.objects.filter(Party=id)
                    Partycustomerdata.delete()
                    PartyCustomerMapping_Serializer.save()
                    log_entry = create_transaction_logNew(request, PartyCustomerMappingMaster_data,id,'',340,0,0,PartyCustomerMapping_Serializer.data[0]['Customer'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyMaster Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, PartyCustomerMappingMaster_data,id,'PartyMasterSave:'+str(PartyCustomerMapping_Serializer.errors),34,0,0,PartyCustomerMapping_Serializer.data[0]['Customer'])
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PartyCustomerMapping_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartyCustomerMappingMaster_data, 0,'Party Customer Mapping Save:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_PartySubParty.objects.raw('''SELECT MC_PartySubParty.id,M_Parties.Name as CustomerName ,MC_PartySubParty.Party_id,MC_PartySubParty.SubParty_id 
as Customer,M_PartyCustomerMappingMaster.MapCustomer, MC_PartyAddress.Address as CustomerAddress, M_Parties.GSTIN, M_Routes.Name as RouteName
From MC_PartySubParty 
LEFT join M_PartyCustomerMappingMaster ON M_PartyCustomerMappingMaster.Customer_id = MC_PartySubParty.SubParty_id AND M_PartyCustomerMappingMaster.Party_id = %s
JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id AND MC_PartySubParty.Party_id=%s AND M_Parties.IsApprovedParty = 0
JOIN M_PartyType ON M_PartyType.id=M_Parties.PartyType_id 
LEFT JOIN M_Routes ON   MC_PartySubParty.Route_id = M_Routes.id 
LEFT JOIN MC_PartyAddress ON MC_PartyAddress.Party_id = M_Parties.id AND MC_PartyAddress.IsDefault=1''', ([id],[id]))
                # AND M_PartyType.IsRetailer=1 remove (for credit note upload need all Parties not only Retailer)
                
                if query:
                    Party_Serializer = PartyCustomerMappingSerializerSecond(query,many=True).data
                    log_entry = create_transaction_logNew(request, Party_Serializer,Party_Serializer[0]['Party_id'],'PartyCustomerMapping',341,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Party_Serializer})
                log_entry = create_transaction_logNew(request,0,0,'Party Does Not Exist',341,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Party not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GET Party Customer Mapping:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})


class PartyItemMappingMasterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request):
        ItemsMappingMaster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ItemsMapping_Serializer = ItemMappingMasterSerializer(data=ItemsMappingMaster_data,many=True)
                if ItemsMapping_Serializer.is_valid():
                    id = ItemsMapping_Serializer.data[0]['Party']
                    ItemsMappingdata = M_ItemMappingMaster.objects.filter(Party=id)
                    ItemsMappingdata.delete()
                    ItemsMapping_Serializer.save()
                    log_entry = create_transaction_logNew(request, ItemsMappingMaster_data,id,'',342,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Items Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, ItemsMappingMaster_data,id,'ItemSave:'+str(ItemsMapping_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  ItemsMapping_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ItemsMappingMaster_data, 0,'Party Item Mapping Save:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_PartyItems.objects.raw('''SELECT MC_PartyItems.id, MC_PartyItems.Item_id,MC_PartyItems.Party_id,M_Items.Name,M_ItemMappingMaster.MapItem FROM MC_PartyItems LEFT JOIN M_ItemMappingMaster ON M_ItemMappingMaster.Party_id=MC_PartyItems.Party_id AND MC_PartyItems.Item_id=M_ItemMappingMaster.Item_id JOIN M_Items ON M_Items.id = MC_PartyItems.Item_id Where MC_PartyItems.Party_id=%s''',([id]))
                
                if query:
                    ItemsMapping_Serializer = ItemMappingMasterSerializerSecond(query,many=True).data
                    log_entry = create_transaction_logNew(request, ItemsMapping_Serializer,0,'',343,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :ItemsMapping_Serializer})
                log_entry = create_transaction_logNew(request,0,0,'Item Does Not Exist',343,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GET Party Item Mapping:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

class PartyUnitMappingMasterUnitsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self,request):
        UnitsMappingMaster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UnitsMapping_Serializer = UnitsMappingSerializer(data= UnitsMappingMaster_data,many=True)
                if UnitsMapping_Serializer.is_valid():
                    id = UnitsMapping_Serializer.data[0]['Party']
                    UnitsMappingdata = M_UnitMappingMaster.objects.filter(Party=id)
                    UnitsMappingdata.delete()
                    UnitsMapping_Serializer.save()
                    log_entry = create_transaction_logNew(request, UnitsMappingMaster_data,id,'',344,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Units Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, UnitsMappingMaster_data,id,'UnitSave:'+str(UnitsMapping_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  UnitsMapping_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, UnitsMappingMaster_data, 0,'Party Mapping Unit Save:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Units.objects.raw('''SELECT M_Units.id,M_Units.Name,M_UnitMappingMaster.MapUnit,M_UnitMappingMaster.Party_id FROM M_Units Left JOIN M_UnitMappingMaster ON M_UnitMappingMaster.Unit_id = M_Units.id AND M_UnitMappingMaster.Party_id=%s''',([id]))

                if query:
                    UnitsMapping_Serializer = UnitsMappingSerializerSecond(query,many=True).data
                    log_entry = create_transaction_logNew(request, UnitsMapping_Serializer,0,'',345,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :UnitsMapping_Serializer})
                log_entry = create_transaction_logNew(request,0,0,'Unit Does Not Exist',345,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Unit not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GET Party Mapping Unit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

        
    