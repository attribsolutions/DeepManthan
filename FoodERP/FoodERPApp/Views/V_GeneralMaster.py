from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GeneralMaster import *
from ..Views.V_CommFunction import *

class ReceiptModeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                ReceiptJsondata = JSONParser().parse(request)
                CompanyID = ReceiptJsondata['Company']
                ReceiptmodeQuery = M_GeneralMaster.objects.filter(Company__in=[1,CompanyID]).filter(TypeID=3)
                
                if ReceiptmodeQuery.exists():
                    Receiptdata = GeneralMasterserializer(ReceiptmodeQuery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Receiptdata})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Receipt Mode Not available ', 'Data': []})
        except M_GeneralMaster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Receipt Mode Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

#List API View

class GeneralMasterFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        GeneralMasterdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Company = GeneralMasterdata['Company']
                query = M_GeneralMaster.objects.filter(Company=Company)
                if query:
                    GeneralMaster_Serializer = GeneralMasterserializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_Serializer})
                    GeneralMaster_SerializerList = list()
                    for a in GeneralMaster_Serializer:
                        type=a['TypeID']
                        query2 =M_GeneralMaster.objects.filter(id=type).values('Name')
                        if type == 0:
                            TypeName='NewGeneralMasterType'
                        else:
                            TypeName=query2[0]['Name']     
                        GeneralMaster_SerializerList.append({
                        "id": a['id'],
                        "TypeID": a['TypeID'],
                        "TypeName":TypeName,
                        "Name": a['Name'],
                        "IsActive": a['IsActive'],
                        "Company": a['Company']['id'],
                        "CompanyName":a['Company']['Name']
                        }) 
                    log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'',240,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_SerializerList })
                log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMasterList Not Found',240,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMasterList:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
            


#Get General Master Type -Post API             
class GeneralMasterTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        GeneralMasterdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                CompanyID = GeneralMasterdata['Company']
                if (CompanyID >1):
                    query = M_GeneralMaster.objects.filter(Company=1,TypeID=0)    
                    GeneralMaster_Serializer = GeneralMasterserializer(query, many=True).data
                    GeneralMaster_SerializerList = list()
                    for a in GeneralMaster_Serializer:   
                        GeneralMaster_SerializerList.append({
                        "id":a['id'],    
                        "TypeID": a['TypeID'],
                        "Name": a['Name']   
                        })
                else:
                    query = M_GeneralMaster.objects.filter(Company=1,TypeID=0)    
                    GeneralMaster_Serializer = GeneralMasterserializer(query, many=True).data
                    GeneralMaster_SerializerList = list()
                    for a in GeneralMaster_Serializer:   
                        GeneralMaster_SerializerList.append({
                        "id":a['id'],    
                        "TypeID": a['TypeID'],
                        "Name": a['Name']   
                        })
                    GeneralMaster_SerializerList.append({"id":"0","Name":"NewGeneralMasterType"})
                log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'CompanyID:'+str(CompanyID),241,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_SerializerList})
        except Exception as e:
                log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMasterType:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})              


#Get General Master Type -Post API             
class GeneralMasterSubTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        GeneralMasterdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Company = GeneralMasterdata['Company'] 
                Type = GeneralMasterdata['TypeID'] 
                query = M_GeneralMaster.objects.filter(Company__in=[1,Company],TypeID=Type,IsActive = 1)
                GeneralMaster_Serializer = GeneralMasterserializer(query, many=True).data
                GeneralMaster_SerializerList = list()
                for a in GeneralMaster_Serializer:   
                    GeneralMaster_SerializerList.append({
                    "id":a['id'],    
                    "Name": a['Name']   
                    })
                # GeneralMaster_SerializerList.append({"id":"0","Name":"NewGeneralMasterType"})  
                log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'Company:'+str(Company),242,0)   
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': GeneralMaster_SerializerList})
        except Exception as e:
                log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMasterSubType:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
    
    
#Post API - Save API 
class GeneralMasterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication                      

    @transaction.atomic()
    def post(self, request):
        GeneralMasterdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GeneralMaster_Serializer = GeneralMasterserializer(data=GeneralMasterdata)
                if GeneralMaster_Serializer.is_valid():
                    GeneralMaster = GeneralMaster_Serializer.save()
                    LastInsertID = GeneralMaster.id
                    log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'Company:'+str(GeneralMasterdata['Company'])+','+'TransactionID:'+str(LastInsertID),243,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Genearl Master Save Successfully', 'TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GenearlMasterSave:'+str(GeneralMaster_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':GeneralMaster_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GenearlMasterSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
            
class GeneralMasterViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = M_GeneralMaster.objects.filter(id=id)
                if query.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    GeneralMasterdata = GeneralMasterserializer(query, many=True).data
                    GeneralMasterList=list()
                    for a in GeneralMasterdata:
                        type=a['TypeID']
                        query2 =M_GeneralMaster.objects.filter(id=type).values('Name')
                        if type == 0:
                            TypeName='NewGeneralMasterType'
                        else:
                            TypeName=query2[0]['Name']
                        
                        GeneralMasterList.append({
                            "id": a['id'],
                            "TypeID": a['TypeID'],
                            "TypeName":TypeName,
                            "Name": a['Name'],
                            "IsActive": a['IsActive']
                        })
                    log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'TransactionID:'+str(id),244,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GeneralMasterList[0]})
                log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMaster Not available',244,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'General Master data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'SingleGETGeneralMaster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        GeneralMasterdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GeneralMasterdataByID = M_GeneralMaster.objects.get(id=id)
                GeneralMaster_Serializer = GeneralMasterserializer(
                    GeneralMasterdataByID, data=GeneralMasterdata)
                if GeneralMaster_Serializer.is_valid():
                    GeneralMaster = GeneralMaster_Serializer.save()
                    LastInsertID = GeneralMaster.id
                    log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMasterEdit:'+str(LastInsertID),245,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'General Master Updated Successfully','TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMasterEdit:'+str(GeneralMaster_Serializer.errors),245,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': GeneralMaster_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,GeneralMasterdata, 0,'GeneralMasterEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                GeneralMasterdata = M_GeneralMaster.objects.filter(TypeID=id).count()
                if GeneralMasterdata == 0:
                    GeneralMasterdata = M_GeneralMaster.objects.get(id=id)
                    GeneralMasterdata.delete()
                    log_entry = create_transaction_logNew(request,{"GeneralMasterID":id}, 0,'GeneralMasterDeleteID:'+str(id),246,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'General Master Deleted Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,0, 0,'GeneralMasterDelete:'+'GeneralMaster Used in another table',8,0)
                    return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This is used in another transaction', 'Data':[]}) 
        except IntegrityError:   
            log_entry = create_transaction_logNew(request,0, 0,'GeneralMasterDelete:'+'GeneralMaster Used in another table',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'General Master used in another table', 'Data': []})   

class GeneralMasterBrandName(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request, id=0 ):
        BrandDetailsdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Company = BrandDetailsdata['Company']
                Type = BrandDetailsdata['TypeID']
                query = M_GeneralMaster.objects.filter(Company_id = Company,TypeID=Type)
                # return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': str(query.query)}) 
                if not query:
                    log_entry = create_transaction_logNew(request,BrandDetailsdata, 0,'Items Not available',34,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = GeneralMasterserializer(query, many=True).data
                    ListData = list ()
                    for a in Items_Serializer:
                        ListData.append({
                            "id": a['id'],
                            "Name": a['Name']       
                        }) 
                    log_entry = create_transaction_logNew(request,BrandDetailsdata, 0,'Company:'+str(Company),247,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': ListData})   
        except Exception as e:
            log_entry = create_transaction_logNew(request,BrandDetailsdata, 0,'GeneralMasterBrandName:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []}) 
        
        
        
        
              