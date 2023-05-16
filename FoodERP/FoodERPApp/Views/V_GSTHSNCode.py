from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GSTHSNCode import *
from ..Serializer.S_Items import *
from .V_CommFunction import *
from ..models import *

class M_GstHsnCodeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                GstHsndata = M_GSTHSNCode.objects.raw('''SELECT M_GSTHSNCode.id,M_GSTHSNCode.EffectiveDate,M_GSTHSNCode.Company_id,M_GSTHSNCode.CommonID,M_GSTHSNCode.CreatedBy,M_GSTHSNCode.CreatedOn,C_Companies.Name CompanyName  FROM M_GSTHSNCode left join C_Companies on C_Companies.id = M_GSTHSNCode.Company_id where M_GSTHSNCode.CommonID > 0 AND M_GSTHSNCode.IsDeleted=0  group by EffectiveDate,CommonID Order BY EffectiveDate Desc''')
                # print(str(MRPdata.query))
                if not GstHsndata:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'GST And HSNCode Not available', 'Data': []})
                else:
                    GstHsndata_Serializer = M_GstHsnCodeSerializer(GstHsndata, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GstHsndata_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GstHsnCodedata = JSONParser().parse(request)
                a=MaxValueMaster(M_GSTHSNCode,'CommonID')
                jsondata=a.GetMaxValue() 
                additionaldata= list()
                for b in GstHsnCodedata:
                    b.update({"CommonID": jsondata})
                    additionaldata.append(b)
                M_GstHsncodeSerializer = M_GstHsnCodeSerializer(data=additionaldata,many=True)
            if M_GstHsncodeSerializer.is_valid():
                M_GstHsncodeSerializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GST HsnCode Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_GstHsncodeSerializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})



''' GST HSNCode Master List Delete Api Depend on ID '''
class M_GSTHSNCodeViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GSTHSNCodedata = M_GSTHSNCode.objects.filter(id=id).update(IsDeleted=1)
                # GSTHSNCodedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GST and HSNCode Deleted Successfully','Data':[]})
        except M_GSTHSNCode.DoesNotExist:
            transaction.set_rollback(True)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'GST and HSNCode  Not available', 'Data': []})
        except IntegrityError:
            transaction.set_rollback(True)   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'GST and HSNCode  used in another table', 'Data': []}) 


''' GST HSNCode Master List Delete Api Depend on CommonID '''
class M_GSTHSNCodeViewThird(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        Query = M_GSTHSNCode.objects.filter(CommonID=id)
        # return JsonResponse({'StatusCode': 200, 'Status': True,'Data':str(Query.query)})
        GSTHSNCode_Serializer = M_GstHsnCodeSerializer(Query, many=True).data
        for a in GSTHSNCode_Serializer:
            deletedID = a['id']
            try:
                with transaction.atomic():
                    GSTHSNCodedata = M_GSTHSNCode.objects.filter(id=deletedID).update(IsDeleted = 1)   
            except M_GSTHSNCode.DoesNotExist:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'GST and HSNCode  Not available', 'Data': []})         
            except IntegrityError:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'GST and HSNCode used in another table', 'Data': []}) 
        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GST and HSNCode Deleted Successfully','Data':[]})

class GETGstHsnDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                EffectiveDate = request.data['EffectiveDate']
                query = M_Items.objects.all()
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = M_ItemsSerializer01(query, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        Item= a['id']
                        b=GSTHsnCodeMaster(Item,EffectiveDate)
                        TodaysGstHsnCode=b.GetTodaysGstHsnCode()
                        EffectiveDateGstHsnCode=b.GetEffectiveDateGstHsnCode()
                        ID=b.GetEffectiveDateGstHsnID()
                        ItemList.append({
                            "id":ID,
                            "Item": Item,
                            "Name": a['Name'],
                            "CurrentGSTPercentage":TodaysGstHsnCode[0]["GST"],
                            "GSTPercentage":EffectiveDateGstHsnCode[0]["GST"],
                            "CurrentHSNCode":TodaysGstHsnCode[0]["HSNCode"],
                            "HSNCode":EffectiveDateGstHsnCode[0]["HSNCode"],
                          
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
           