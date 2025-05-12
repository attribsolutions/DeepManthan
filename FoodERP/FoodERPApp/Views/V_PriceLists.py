from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PriceLists import *
from ..models import *
from ..Views.V_CommFunction import *

def CalculationPathLable(CalculationPathSting):
    
    if CalculationPathSting == '':
        CalculationPathdata=[]
    else:    
        w=CalculationPathSting.split(",")
       
        CalculationPathdata=list()
        for p in w:
            query=M_PriceList.objects.filter(id=p).values('id','Name')
            CalculationPathdata.append({
                "id" :query[0]['id'],
                "Name" : query[0]['Name']   
            })
    
    return CalculationPathdata

def getchildnode(ParentID):
    
    Modulesdata = M_PriceList.objects.filter(BasePriceListID=ParentID)
    cdata=list()
    if Modulesdata.exists():
        Modules_Serializer = PriceListSerializer(Modulesdata, many=True).data
       
        for z in Modules_Serializer:
        
            cchild=getchildnode(z["id"])
            cdata.append({
                
                "value":z["id"],
                "label":z["Name"],
                "MkUpMkDn":z["MkUpMkDn"],
                "BasePriceListID" :z['BasePriceListID'],
                "CalculationPath":CalculationPathLable(z['CalculationPath']),

                "children":cchild
            })
        return cdata
    else:
        return []

class CompanywisePriceListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,Company=0):
        try:
            with transaction.atomic():
              
                query = M_PriceList.objects.filter(Company=Company)
               
                # return JsonResponse({'StatusCode': 204, 'Status': True,'Data':str(query.query)})
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List Not available', 'Data': []})
                else:
                    PriceList_Serializer = PriceListSerializerSecond(
                        query, many=True).data
                    PriceListData = list()
                    for a in PriceList_Serializer:
                        PriceListData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "BasePriceListID": a['BasePriceListID'],
                            "MkUpMkDn": a['MkUpMkDn'],
                            "PLPartyType": a['PLPartyType']['id'],
                            "PLPartyTypeName": a['PLPartyType']['Name'],
                            "Company":a['Company']['id'],
                            "CompanyName":a['Company']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    log_entry = create_transaction_logNew(request,PriceList_Serializer, 0,'Company:'+str(a['Company']['id']),248,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PriceListData})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0, 0,'CompanywisePriceLists:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class PriceListView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PriceListdata = JSONParser().parse(request)
                PriceListdata_Serializer = PriceListSerializer(
                    data=PriceListdata)
                if PriceListdata_Serializer.is_valid():
                    PriceList = PriceListdata_Serializer.save()
                    LastInsertID = PriceList.id
                    log_entry = create_transaction_logNew(request,PriceListdata, 0,'Company:'+str(PriceListdata['Company'])+','+'TransactionID:'+str(LastInsertID),249,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Price List Save Successfully','TransactionID':LastInsertID, 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,PriceListdata, 0,'PriceListSave:'+str(PriceListdata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PriceListdata_Serializer.errors, 'Data': []})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0, 0,'PriceListSave:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_PriceList.objects.all()
                if query:
                    Pricelist_serializer = PriceListSerializer(query, many=True).data
                    log_entry = create_transaction_logNew(request, Pricelist_serializer,0,'',284,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Pricelist_serializer})
                log_entry = create_transaction_logNew(request, Pricelist_serializer,0,'PriceList not available',284,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'PriceList not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'PriceList:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class PriceListViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_PriceList.objects.filter(PLPartyType_id=id,BasePriceListID=0)
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List Not available', 'Data': []})
                else:
                    PriceList_Serializer = PriceListSerializer(query, many=True).data
                   
                    PriceListData = list()
                    for a in PriceList_Serializer:
                       
                        aa=a['id']
                        
                        child=getchildnode(aa)
                        PriceListData.append({ 
                            "value": a['id'],
                            "label": a['Name'],
                            "MkUpMkDn":a["MkUpMkDn"],
                            "BasePriceListID" :a['BasePriceListID'],
                            "CalculationPath":CalculationPathLable(a['CalculationPath']),

                            "children":child
                            })
                log_entry = create_transaction_logNew(request,PriceList_Serializer, 0,'TransactionID:'+str(id),250,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PriceListData})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0, 0,'SinglePriceList'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                PriceListdata = JSONParser().parse(request)
                PriceListdataID = M_PriceList.objects.get(id=id)
                PriceListdata_Serializer = PriceListSerializer(
                    PriceListdataID, data=PriceListdata)
                if PriceListdata_Serializer.is_valid():
                    PriceListdata_Serializer.save()
                    log_entry = create_transaction_logNew(request,PriceListdata, 0,'TransactionID:'+str(id),251,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Price List Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,PriceListdata, 0,'PriceListEdit:'+str(PriceListdata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PriceListdata_Serializer.errors, 'Data': []})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0, 0,'PriceListEdit:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PriceListdata = M_PriceList.objects.get(id=id)
                PriceListdata.delete()
                log_entry = create_transaction_logNew(request,{"PriceListID":id}, 0,'PriceListDeleteID:'+str(id),252,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Price List Deleted Successfully', 'Data': []})
        except M_PriceList.DoesNotExist:
            log_entry = create_transaction_logNew(request,0, 0,'Price List Not available',252,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request,0, 0,'PriceListDeleteID:'+str(id),8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List used in another table', 'Data': []})