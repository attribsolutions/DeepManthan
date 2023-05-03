from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyItems import *
from ..models import *


class PartyItemsListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_PartyItems.objects.raw(
                    '''select MC_PartyItems.id,M_Parties.Name, MC_PartyItems.Party_id,count(MC_PartyItems.Item_id)As Total From MC_PartyItems join M_Parties on M_Parties.id=MC_PartyItems.Party_id group by MC_PartyItems.Party_id  ''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = MC_PartyItemListSerializer(
                        query, many=True).data
                    # return JsonResponse({ 'query': Items_Serializer[0]})
                    ItemList = list()
                    for a in Items_Serializer:
                        ItemList.append({
                            "id": a['Party_id'],
                            "Name": a['Name'],
                            "Total": a['Total']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class PartyItemsFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
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
                
                    Itemquery= MC_PartyItems.objects.raw('''SELECT M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName from M_Items left JOIN MC_PartyItems ON MC_PartyItems.item_id=M_Items.id AND MC_PartyItems.Party_id=%s left JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id where IsSCM=1 and M_Items.Company_id in (select id from C_Companies where CompanyGroup_id=%s ) ''',([PartyID],[CompanyGroupID]))
                else:
                    Itemquery= MC_PartyItems.objects.raw('''SELECT M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName from M_Items left JOIN MC_PartyItems ON MC_PartyItems.item_id=M_Items.id AND MC_PartyItems.Party_id=%s left JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id where Company_id =%s ''',([PartyID],[CompanyID]))
               
                
                
                print(str(Itemquery.query))
                if not Itemquery:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = MC_PartyItemSerializerSingleGet(
                        Itemquery, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        ItemList.append({
                            "Item": a['id'],
                            "ItemName": a['Name'],
                            "Party": a['Party_id'], 
                            "PartyName": a['PartyName'],
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class PartyItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    
    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PartyItems_data = JSONParser().parse(request)
                PartyItems_serializer = MC_PartyItemSerializer(
                    data=PartyItems_data, many=True)
            if PartyItems_serializer.is_valid():
                id = PartyItems_serializer.data[0]['Party']
                MC_PartyItem_data = MC_PartyItems.objects.filter(Party=id)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :str(MC_PartyItem_data.query)})
                MC_PartyItem_data.delete()
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :PartyItems_serializer.data[0]['Party']})
                PartyItems_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data': []})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyItems_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
