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
    def get(self, request):
        try:
            with transaction.atomic():
                MRPdata = M_MRPMaster.objects.raw('''SELECT M_MRPMaster.id,M_MRPMaster.EffectiveDate,M_MRPMaster.Company_id,M_MRPMaster.Division_id,M_MRPMaster.Party_id,M_MRPMaster.CreatedBy,M_MRPMaster.CreatedOn,M_MRPMaster.CommonID,C_Companies.Name CompanyName,a.Name DivisionName,M_Parties.Name PartyName  FROM M_MRPMaster left join C_Companies on C_Companies.id = M_MRPMaster.Company_id left join M_Parties a on a.id = M_MRPMaster.Division_id left join M_Parties on M_Parties.id = M_MRPMaster.Party_id where M_MRPMaster.CommonID >0 AND M_MRPMaster.IsDeleted=0   group by EffectiveDate,Party_id,Division_id,CommonID Order BY EffectiveDate Desc''')
                # print(str(MRPdata.query))
                if not MRPdata:
                    log_entry = create_transaction_log(request, 0, 0, 0, "MRP Not available",7,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'MRP Not available', 'Data': []})
                else:
                    MRPdata_Serializer = M_MRPsSerializerSecond(MRPdata, many=True).data
                    log_entry = create_transaction_log(request, {'MRPDetails':MRPdata_Serializer}, 0, 0, "MRP",119,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MRPdata_Serializer})
        except Exception as e:
            log_entry = create_transaction_log(request, {'MRPDetails':MRPdata_Serializer}, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Mrpsdata = JSONParser().parse(request)
                a=MaxValueMaster(M_MRPMaster,'CommonID')
                jsondata=a.GetMaxValue() 
                additionaldata= list()
                for b in M_Mrpsdata:
                    b.update({'CommonID': jsondata})
                    additionaldata.append(b)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Save Successfully','Data' : additionaldata })
                M_Mrps_Serializer = M_MRPsSerializer(data=additionaldata,many=True)
            if M_Mrps_Serializer.is_valid():
                M_Mrps_Serializer.save()
                LastInsertID = (M_MRPMaster.objects.last()).id
                log_entry = create_transaction_log(request, M_Mrpsdata, 0, 0, "MRP Save Successfully",120,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Save Successfully','Data' :[]})
            else:
                log_entry = create_transaction_log(request, M_Mrpsdata, 0, 0, M_Mrps_Serializer.errors,34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Mrps_Serializer.errors,'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_log(request, M_Mrpsdata, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class GETMrpDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                DivisionID = request.data['Division']
                PartyID = request.data['Party']
                EffectiveDate = request.data['EffectiveDate']
                query = M_Items.objects.all()
                if not query:
                    log_entry = create_transaction_log(request, 0, 0, PartyID, "Items Not available",7,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = M_ItemsSerializer01(query, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        Item= a['id']
                        
                        b=MRPMaster(Item,DivisionID,PartyID,EffectiveDate)
                        TodaysMRP=b.GetTodaysDateMRP()
                        EffectiveDateMRP=b.GetEffectiveDateMRP()
                        ID=b.GetEffectiveDateMRPID()
                        ItemList.append({
                            "id":ID,
                            "Item": Item,
                            "Name": a['Name'],
                            "CurrentMRP": TodaysMRP[0]["TodaysMRP"],
                            "CurrentDate":TodaysMRP[0]["Date"],
                            "MRP": EffectiveDateMRP
                        })
                    log_entry = create_transaction_log(request, {'MRPDetails':Items_Serializer}, 0, PartyID, "MRPDetails",121,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
        except Exception as e:
            log_entry = create_transaction_log(request, {'MRPDetails':Items_Serializer}, 0, PartyID, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

''' MRP Master List Delete Api Depend on ID '''
class M_MRPsViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                MRPdata = M_MRPMaster.objects.filter(id=id).update(IsDeleted=1)
                # MRPdata.delete()
                log_entry = create_transaction_log(request, {'MRPID':id}, 0, 0, "MRP Deleted Successfully",122,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Deleted Successfully','Data':[]})
        except M_MRPMaster.DoesNotExist:
            log_entry = create_transaction_log(request,{'MRPID':id}, 0, 0, "MRP Not available",7,0)
            transaction.set_rollback(True)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_log(request,{'MRPID':id}, 0, 0, "MRP used in another table",8,0)
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
            print(deletedID)
            try:
                with transaction.atomic():
                    MRPdata = M_MRPMaster.objects.filter(id=deletedID).update(IsDeleted=1)
            except M_MRPMaster.DoesNotExist:
                log_entry = create_transaction_log(request, {'MRPID':id}, 0, 0, "MRP Not available",7,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP Not available', 'Data': []})    
            except IntegrityError:
                log_entry = create_transaction_log(request, {'MRPID':id}, 0, 0, "MRP used in another table",8,0)
                transaction.set_rollback(True)   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP used in another table', 'Data': []}) 
        log_entry = create_transaction_log(request, {'MRPID':id}, 0, 0, "DeleteMrpOnList",123,0)
        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Deleted Successfully','Data':[]})
           
            
                

    
           