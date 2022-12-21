from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from django.db.models import Max

from ..Serializer.S_Margins import *

from ..Serializer.S_Items import *

from ..Serializer.S_Parties import *

from .V_CommFunction import *

from ..models import *


class M_MarginsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                Margindata = M_MarginMaster.objects.raw('''SELECT m_marginmaster.id,m_marginmaster.EffectiveDate,m_marginmaster.Company_id,m_marginmaster.PriceList_id,m_marginmaster.CreatedBy,m_marginmaster.CreatedOn,m_marginmaster.Party_id,m_marginmaster.CommonID,c_companies.Name CompanyName, m_pricelist.Name PriceListName,m_parties.Name PartyName  FROM m_marginmaster  left join c_companies on c_companies.id = m_marginmaster.Company_id left join m_pricelist  on m_pricelist.id = m_marginmaster.PriceList_id left join m_parties on m_parties.id = m_marginmaster.Party_id where m_marginmaster.CommonID>0 AND m_marginmaster.IsDeleted=0 group by EffectiveDate,Party_id,PriceList_id,CommonID Order BY EffectiveDate Desc''')
                # print(str(MRPdata.query))
                if not Margindata:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Margindata_Serializer = M_MarginsSerializerSecond(Margindata, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Margindata_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Marginsdata = JSONParser().parse(request)
                a=MaxValueMaster(M_MarginMaster,'CommonID')
                jsondata=a.GetMaxValue()     
                additionaldata= list()
                for b in M_Marginsdata:
                    b.update({'CommonID': jsondata})
                    additionaldata.append(b)     
                M_Margins_Serializer = M_MarginsSerializer(data=additionaldata,many=True)
            if M_Margins_Serializer.is_valid():
                M_Margins_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Margins Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Margins_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class GETMarginDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PriceListID = request.data['PriceList']
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
                        b = MarginMaster(Item,PriceListID,PartyID,EffectiveDate)
                        TodaysMargin=b.GetTodaysDateMargin()
                        EffectiveDateMargin=b.GetEffectiveDateMargin()
                        ID = b.GetEffectiveDateMarginID()
                        ItemList.append({
                            "id": ID,
                            "Item": Item,
                            "Name": a['Name'],
                            "CurrentMargin": TodaysMargin[0]["TodaysMargin"],
                            "CurrentDate":TodaysMargin[0]["Date"],
                            "Margin":EffectiveDateMargin,
                           
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

''' MRP Master List Delete Api Depend on ID '''

class M_MarginsViewSecond(CreateAPIView):   
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Margindata = M_MarginMaster.objects.filter(id=id).update(IsDeleted=1)
                # Margindata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Margin Deleted Successfully','Data':[]})
        except M_MarginMaster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Margin Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Margin used in another table', 'Data': []}) 



''' Margin Master List Delete Api Depend on CommonID '''
class M_MarginsViewThird(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def delete(self, request, id=0):
        Query = M_MarginMaster.objects.filter(CommonID=id)
        # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':str(Query.query)})
        Margin_Serializer = M_MarginsSerializer(Query, many=True).data
        for a in Margin_Serializer:
            deletedID = a['id']
            try:
                with transaction.atomic():
                    Margindata = M_MarginMaster.objects.filter(id=deletedID).update(IsDeleted=1) 
            except M_MarginMaster.DoesNotExist:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Margin Not available', 'Data': []})    
            except IntegrityError:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Margin used in another table', 'Data': []}) 
        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Margin Deleted Successfully','Data':[]})
    