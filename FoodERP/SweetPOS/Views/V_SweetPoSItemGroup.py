import base64
from ..models import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
from FoodERPApp.models import *
from ..Serializer.S_SweetPoSItemGroup import *
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew

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


class ItemGroupandSubgroupView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        try:
            user = BasicAuthenticationfunction(request)
            if user is not None:
                groups = M_Group.objects.filter(GroupType=5)
                response_data = {"status": True, "status_code": 200, "count": groups.count(),"data": [] }              
                
                for group in groups:
                    sequence = group.Sequence if group.Sequence is not None else 0.00
                    group_data = {
                        "CompanyName": group.Name,
                        "POSCompanyID": group.id,
                        "CompanyDisplayName": group.Name,
                        "CompanyDisplayIndex":sequence,
                        "IsActive": True,
                        "Itemsgroup": []
                    }
                    subgroups = MC_SubGroup.objects.filter(Group=group)
                    for subgroup in subgroups:
                        sequence = subgroup.Sequence if subgroup.Sequence is not None else 0.00
                        subgroup_data = {
                            "GroupID": subgroup.id,
                            "ItemName": None, 
                            "GroupName": subgroup.Name,
                            "GroupDisplayName": subgroup.Name,
                            "GroupDisplayIndex": sequence,
                            "IsActive": True,
                        }
                        group_data["Itemsgroup"].append(subgroup_data)
                    response_data["data"].append(group_data)
                log_entry = create_transaction_logNew(request, 0, 0,'ItemGroupandSubgroup',391,0)
                return Response(response_data)
            else:
                log_entry = create_transaction_logNew(request,0, 0, "Item Not available",391,0)
                return Response({'status': False, 'status_code': 401, 'message': 'Unauthorized'}, status=401)
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'ItemGroupandSubgroup:'+str(e),33,0)
            return Response({'status': False, 'status_code': 400, 'message': str(e), 'data': []}, status=400)


class ItemListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    def get(self, request,DivisionID=0):
        try:
            user = BasicAuthenticationfunction(request)
            if user is not None:
                
                query = M_Items.objects.raw(f"""SELECT i.id , i.CItemID AS CItemID, ifnull(i.BarCode,"")BarCode, 
                ifnull(GSTHsnCodeMaster(i.id, CURDATE(), 3,0,0),0) AS HSNCode,i.Name, i.SAPItemCode AS ItemCode,  
                ifnull(Round(GSTHsnCodeMaster(i.id, CURDATE(), 2,0,0),2),0.0)  AS GST,
                ifnull(Round(GetTodaysDateMRP(i.id, CURDATE(), 2, 0, 0,0),2),0.0) AS Rate,
                (select EffectiveDate from M_MRPMaster where id=(ifnull(GetTodaysDateMRP(i.id, CURDATE(), 1, 0, 0,0),0.0)))RateEffectiveDate,                          
                ifnull(i.BaseUnitID_id,0) AS UnitID, i.IsFranchisesItem,  
                ifnull(Round(GetTodaysDateMRP(i.id, CURDATE(), 2, 0,0,0),2),0.0) AS FoodERPMRP,
                ifnull(MC_ItemGroupDetails.SubGroup_id,0) AS ItemGroupID,MC_ItemGroupDetails.ItemSequence,
                i.IsCBMItem ,i.IsMixItem,ifnull(SweetPOS.SPOSRateMaster(i.id),"0,0,0,0")OnlineRates
                FROM M_Items AS i
                left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=i.id and GroupType_id=5
                LEFT JOIN M_ChannelWiseItems ON i.id = M_ChannelWiseItems.Item_id
                join MC_PartyItems on MC_PartyItems.Item_id=i.id and MC_PartyItems.party_id={DivisionID}
                WHERE M_ChannelWiseItems.PartyType_id = 19  """)                  
                # return Response({"status": True, "status_code": 200, "count": "", "data": "" }, status=200)
                # print(query)
                count=0
                item_data=list()
                for row in query:
                   
                    count=count+1
                    Ratelist=list()
                    Ratelist.append({
                            "Rate": row.Rate,
                            "POSRateType": 174,
                            "IsChangeRateToDefault": False,
                            "EffectiveFrom":row.RateEffectiveDate
                    })

                    # queryforRate =M_SPOSRateMaster.objects.filter(ItemID=row.id,IsDeleted=0)
                    # for RateRow in queryforRate:

                    OnlineRates=(row.OnlineRates).split(',') 
                    Ratelist.append({	
                        "Rate": float(OnlineRates[0]),
                        "POSRateType": int(OnlineRates[1]),
                        "IsChangeRateToDefault": bool(OnlineRates[2]),
                        "EffectiveFrom":OnlineRates[3]
                    })
                    
                    
                    item_data.append({
                        "FoodERPID": row.id,
                        "CItemID": row.CItemID,
                        "IsCBMItem" : row.IsCBMItem,
                        "BarCode": row.BarCode,
                        "HSNCode": row.HSNCode,
                        "Name": row.Name,
                        "ItemCode": row.ItemCode,
                        "GST": row.GST,
                        "Rate": Ratelist,
                        "UnitID": row.UnitID,
                        "ISChitaleSupplier": True,  
                        "IsFranchisesPOSItem": row.IsFranchisesItem,
                        "UnitConversion": "",         
                        "FoodERPMRP": row.FoodERPMRP,
                        "ItemGroupID": row.ItemGroupID,
                        "FranchisesItemCode": "" ,
                        "DisplayIndex" :  row.ItemSequence,
                        "IsMixItem" :row.IsMixItem,
                        
                    } )
                    
                log_entry = create_transaction_logNew(request, 0, DivisionID,'ItemList',392,0)
                return Response({"status": True, "status_code": 200, "count": count, "data": item_data }, status=200)
            else:
                log_entry = create_transaction_logNew(request,0, DivisionID, "ItemList Not available",392,0)
                return Response({'status': False, 'status_code': 401, 'message': 'Unauthorized'}, status=401)
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, DivisionID,'ItemList:'+str(e),33,0)
            return Response({'status': False, 'status_code': 400, 'message': Exception(e), 'data': []}, status=400)
