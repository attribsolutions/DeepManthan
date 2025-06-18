from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Mrps import *
from ..Serializer.S_Items import *
from ..Serializer.S_Parties import *
from .V_CommFunction import *
from ..models import *


class M_MRPsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        M_Mrpsdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                a=MaxValueMaster(M_MRPMaster,'CommonID')
                # print("pratiksha")
                # print(a)
                jsondata=a.GetMaxValue() 
                # print("pratik")
                # print("jsondata")
                additionaldata= list()
                for b in M_Mrpsdata:
                    b.update({'CommonID': jsondata})
                    additionaldata.append(b)
                # print(additionaldata)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Save Successfully','Data' : additionaldata })
                M_Mrps_Serializer = M_MRPsSerializer(data=additionaldata,many=True)
                
            if M_Mrps_Serializer.is_valid():
                MRP = M_Mrps_Serializer.save()
                LastInsertID = MRP[0].id
                log_entry = create_transaction_logNew(request, M_Mrpsdata,0,'TransactionID:'+str(LastInsertID),120,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Save Successfully', 'TransactionID':LastInsertID,'ItemID':M_Mrpsdata[0]['Item'],'Data' :[]})
            else:
                log_entry = create_transaction_logNew(request, M_Mrpsdata, 0,'MRPSave:'+str(M_Mrps_Serializer.errors),34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Mrps_Serializer.errors,'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, M_Mrpsdata, 0,'MRPSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class GETMrpDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        MRPDetails = JSONParser().parse(request)
        try:
            with transaction.atomic():
                DivisionID = MRPDetails['Division']
                PartyID = MRPDetails['Party']
                PartyTypeID = MRPDetails['PartyTypeID']
                EffectiveDate = MRPDetails['EffectiveDate']
                CompanyID = MRPDetails['CompanyID']
                today = date.today()
                
                if PartyTypeID == 0 :
                    partytype=(f"AND PartyType_id is null ")
                else:
                    partytype = (f" AND PartyType_id={PartyTypeID}")
                    
                if PartyID == 0 :
                    Partyy=(f"AND Party_id is null ")
                else:
                    Partyy = (f" AND Party_id={PartyID}")
                
                
                
                query = M_Items.objects.raw(f'''SELECT M_Items.id, M_Items.Name AS ItemName,
                                             ifnull(GetTodaysDateMRP(M_Items.id,%s,2,{DivisionID},{PartyID},{PartyTypeID}),0)MRP,
                                             ifnull(GetTodaysDateMRP(M_Items.id,%s,3,{DivisionID},{PartyID},{PartyTypeID}),'')EffectiveDate,
                                             (SELECT ifnull(MRP,0)MRP FROM M_MRPMaster where Item_id=M_Items.id
				                            and EffectiveDate = %s   {Partyy}  {partytype} and IsDeleted=0 order by EffectiveDate desc, id desc limit 1)TodaysDateMRPP,
                                             (SELECT ifnull(id,0)id FROM M_MRPMaster where Item_id=M_Items.id
				                            and EffectiveDate = %s   {Partyy}  {partytype} and IsDeleted=0 order by EffectiveDate desc, id desc limit 1)IDD
                                             From M_Items
                                             WHERE Company_id = {CompanyID}''',[today,today,EffectiveDate,EffectiveDate])             
                # print(query)
                if not query:
                    log_entry = create_transaction_logNew(request, 0, PartyID, "Items Not available",121,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                
                ItemList = list()
                for a in query:
                        ItemList.append({
                            "id":a.IDD,
                            "Item": a.id,
                            "Name": a.ItemName,
                            "CurrentMRP": round(float(a.MRP),2),
                            "CurrentDate":a.EffectiveDate,
                            "MRP": a.TodaysDateMRPP,
                        })
                log_entry = create_transaction_logNew(request,MRPDetails, PartyID,'',121,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
        except Exception as e:
            log_entry = create_transaction_logNew(request,MRPDetails, 0,'GetMRPmethod:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

''' MRP Master List Delete Api Depend on ID '''
class M_MRPsViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                MRPdata = M_MRPMaster.objects.filter(id=id).update(IsDeleted=1)
  
                # print(MRPdata)
                # MRPdata.delete()
                log_entry = create_transaction_logNew(request, {'MRPID':id}, 0, 'MRPID:'+str(id),122,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Deleted Successfully','DeleteID':id,'Data':[]})
        except M_MRPMaster.DoesNotExist:
            log_entry = create_transaction_logNew(request,0, 0, "MRP Not available",122,0)
            transaction.set_rollback(True)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request,0, 0, "MRP used in another table",8,0)
            transaction.set_rollback(True)   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP used in another table', 'Data': []}) 


''' MRP Master List Delete Api Depend on CommonID '''
class M_MRPsViewThird(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        Query = M_MRPMaster.objects.filter(CommonID=id)
        # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':str(Query.query)})
        MRP_Serializer = M_MRPsSerializer(Query, many=True).data
        # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':MRP_Serializer})
        for a in MRP_Serializer:
            deletedID = a['id'] 
            # CustomPrint(deletedID)
            try:
                with transaction.atomic():
                    MRPdata = M_MRPMaster.objects.filter(id=deletedID).update(IsDeleted=1)
            except M_MRPMaster.DoesNotExist:
                log_entry = create_transaction_logNew(request, 0, 0, "MRP Not available",123,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP Not available', 'Data': []})    
            except IntegrityError:
                log_entry = create_transaction_logNew(request, 0, 0, "MRP used in another table",8,0)
                transaction.set_rollback(True)   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP used in another table', 'Data': []}) 
        log_entry = create_transaction_logNew(request, {'MRPID':id}, 0,'MRPID:'+str(id),123,0)
        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Deleted Successfully','DeleteID':id,'Data':[]})
          
class GetMRPListDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,) 
     
    @transaction.atomic()
    def post(self, request):
        MRPListData=JSONParser().parse(request)
        try:
            with transaction.atomic():
                EffectiveDate = MRPListData['EffectiveDate']
                CommonID = MRPListData['CommonID'] 
                
                ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(0,1).split('!')
                  
                query = M_MRPMaster.objects.raw(f'''
                   SELECT M_MRPMaster.id,M_MRPMaster.EffectiveDate,M_MRPMaster.MRP,M_MRPMaster.CommonID,C_Companies.Name CompanyName,
                   M_Items.Name as ItemName, SUM(COUNT(M_Items.id)) OVER () AS ItemCount
                        FROM M_MRPMaster 
                        left join C_Companies on C_Companies.id = M_MRPMaster.Company_id 
                        left join M_Parties a on a.id = M_MRPMaster.Division_id 
                        left join M_Parties on M_Parties.id = M_MRPMaster.Party_id 
                        left join M_PartyType on M_PartyType.id = M_MRPMaster.PartyType_id
                        left join M_Items on M_MRPMaster.Item_id=M_Items.id
                        {ItemsGroupJoinsandOrderby[1]}
                        where M_MRPMaster.IsDeleted=0  
                        AND M_MRPMaster.EffectiveDate=%s AND M_MRPMaster.CommonID=%s
                        GROUP BY M_MRPMaster.id, M_MRPMaster.EffectiveDate, M_MRPMaster.MRP, M_MRPMaster.CommonID, C_Companies.Name, M_Items.Name
                        {ItemsGroupJoinsandOrderby[2]}''',[EffectiveDate,CommonID])    
                
                if query:
                    List = []
                    ItemCount = query[0].ItemCount
                    for a in query:
                        List.append({
                            "id": a.id,
                            "EffectiveDate": a.EffectiveDate,
                            "MRP": a.MRP,
                            "CommonID": a.CommonID,
                            "CompanyName": a.CompanyName,
                            "ItemName": a.ItemName
                        })
                    
                    MRPList = ({
                        "ItemCount":ItemCount,
                        "MRPList": List
                    })

                    log_entry = create_transaction_logNew(request, MRPListData, 0, '', 406, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MRPList})
                else:
                        log_entry = create_transaction_logNew(request, 0, 0, "Get MRP Details:"+"MRP Details Not available", 7, 0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'MRP Details not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, MRPListData, 0, "Get MRP Details:"+ str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []}) 
                


class M_MRPsListViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        MRPListData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = MRPListData['FromDate']
                ToDate = MRPListData['ToDate']
                # M_MRPMaster.CommonID >0 Comment on 21-08-2024
                # MRPdata = M_MRPMaster.objects.raw('''SELECT M_MRPMaster.id,M_MRPMaster.EffectiveDate,M_MRPMaster.Company_id,M_MRPMaster.Division_id,M_MRPMaster.Party_id,M_MRPMaster.CreatedBy,M_MRPMaster.CreatedOn,M_MRPMaster.CommonID,C_Companies.Name CompanyName,a.Name DivisionName,M_Parties.Name PartyName  FROM M_MRPMaster left join C_Companies on C_Companies.id = M_MRPMaster.Company_id left join M_Parties a on a.id = M_MRPMaster.Division_id left join M_Parties on M_Parties.id = M_MRPMaster.Party_id where M_MRPMaster.CommonID >0 AND M_MRPMaster.IsDeleted=0   group by EffectiveDate,Party_id,Division_id,CommonID Order BY EffectiveDate Desc''')
                
                MRPdata = M_MRPMaster.objects.raw('''SELECT M_MRPMaster.id,M_MRPMaster.EffectiveDate,M_MRPMaster.Company_id,
                                                  M_MRPMaster.Division_id,M_MRPMaster.Party_id,M_MRPMaster.PartyType_id,M_MRPMaster.CreatedBy,M_MRPMaster.CreatedOn,
                                                  M_MRPMaster.CommonID,C_Companies.Name CompanyName,a.Name DivisionName,M_Parties.Name PartyName, M_PartyType.Name PartyTypeName  
                                                  FROM M_MRPMaster 
                                                  left join C_Companies on C_Companies.id = M_MRPMaster.Company_id
                                                  left join M_Parties a on a.id = M_MRPMaster.Division_id 
                                                  left join M_Parties on M_Parties.id = M_MRPMaster.Party_id
                                                  left join M_PartyType on M_PartyType.id = M_MRPMaster.PartyType_id
                                                  where M_MRPMaster.IsDeleted=0 AND EffectiveDate BETWEEN %s AND %s 
                                                  group by EffectiveDate,Party_id,Division_id,CommonID
                                                  Order BY EffectiveDate Desc''',[FromDate,ToDate])
                
                if not MRPdata:
                    log_entry = create_transaction_logNew(request, 0, 0, "MRP Not available",119,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'MRP Not available', 'Data': []})
                else:
                    MRPdata_Serializer = M_MRPsSerializerSecond(MRPdata, many=True).data
                    log_entry = create_transaction_logNew(request, MRPdata_Serializer, 0,'',119,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MRPdata_Serializer})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'SingleGET MRP:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})   
           