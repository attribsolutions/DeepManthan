from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Mrps import *

from ..Serializer.S_Items import *

from ..Serializer.S_Parties import *

from .V_CommFunction import *

from ..models import *


class M_MRPsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                MRPdata = M_MRPMaster.objects.raw('''SELECT m_mrpmaster.id,m_mrpmaster.EffectiveDate,m_mrpmaster.Company_id,m_mrpmaster.Division_id,m_mrpmaster.Party_id,m_mrpmaster.CreatedBy,m_mrpmaster.CreatedOn,m_mrpmaster.CommonID,c_companies.Name CompanyName,a.Name DivisionName,m_parties.Name PartyName  FROM m_mrpmaster left join c_companies on c_companies.id = m_mrpmaster.Company_id left join m_parties a on a.id = m_mrpmaster.Division_id left join m_parties on m_parties.id = m_mrpmaster.Party_id where m_mrpmaster.CommonID >0 AND m_mrpmaster.IsDeleted=0   group by EffectiveDate,Party_id,Division_id,CommonID Order BY EffectiveDate Desc''')
                # print(str(MRPdata.query))
                if not MRPdata:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'MRP Not available', 'Data': []})
                else:
                    MRPdata_Serializer = M_MRPsSerializerSecond(MRPdata, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MRPdata_Serializer})
        except Exception as e:
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
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Mrps_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class GETMrpDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                DivisionID = request.data['Division']
                PartyID = request.data['Party']
                EffectiveDate = request.data['EffectiveDate']
                query = M_Items.objects.all()
                if not query:
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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

''' MRP Master List Delete Api Depend on ID '''
class M_MRPsViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                MRPdata = M_MRPMaster.objects.filter(id=id).update(IsDeleted=1)
                # MRPdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Deleted Successfully','Data':[]})
        except M_MRPMaster.DoesNotExist:
            transaction.set_rollback(True)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP Not available', 'Data': []})
        except IntegrityError:
            transaction.set_rollback(True)   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP used in another table', 'Data': []}) 


''' MRP Master List Delete Api Depend on CommonID '''
class M_MRPsViewThird(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

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
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP Not available', 'Data': []})    
            except IntegrityError:
                transaction.set_rollback(True)   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'MRP used in another table', 'Data': []}) 
        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Deleted Successfully','Data':[]})
           
            
                

    
           