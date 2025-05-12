from ..models import *
from ..Serializer.S_BankMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_ImportField import *
from django.db.models import Q
from ..Views.V_CommFunction import *


class ImportFieldListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        ImportField_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                Company = ImportField_data['CompanyID']
                query = M_ImportFields.objects.all()
                if query:
                    Import_serializer = ImportFieldSerializerSecond(query, many=True).data
                    ImportField_List = list()
                    for a in Import_serializer:
                     ImportField_List.append({
                    "id": a['id'],
                    "FieldName": a['FieldName'],
                    "ControlTypeID": a['ControlType']['id'],
                    "ControlTypeName": a['ControlType']['Name'],
                    "FieldValidationID": a['FieldValidation']['id'],
                    "FieldValidationName": a['FieldValidation']['Name'],
                    "IsCompulsory": a['IsCompulsory'],
                    "ImportExcelTypeID":a['ImportExcelType']['id'],
                    "ImportExcelTypeName":a['ImportExcelType']['Name'],     
                })
                    log_entry = create_transaction_logNew(request, ImportField_data, 0, "Company:"+str(Company),395,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :ImportField_List})
                log_entry = create_transaction_logNew(request, ImportField_data, 0, "ImportFieldList:"+"ImportField not available",8,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'ImportField not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ImportField_data, 0,"ImportFieldList:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
class ImportFieldSaveView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        ImportField_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ImportField_serializer = ImportFieldSerializer(
                    data=ImportField_data)
                if ImportField_serializer.is_valid():
                    ImportFieldID = ImportField_serializer.save()
                    LastInsertID = ImportFieldID.id
                    
                    log_entry = create_transaction_logNew(request, ImportField_data,0 ,"",396,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ImportField Save Successfully', 'Data': []})
            log_entry = create_transaction_logNew(request, ImportField_data, 0,"ImportFieldSave:"+str(ImportField_serializer.errors),34,0)
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ImportField_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ImportField_data, 0, "ImportFieldSave:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ImportField_data = M_ImportFields.objects.get(id=id)
                ImportField_serializer = ImportFieldSerializerSecond(

                    ImportField_data).data
                ImportField_List = list()
                ImportField_List.append({
                    "id": ImportField_serializer['id'],
                    "FieldName": ImportField_serializer['FieldName'],
                    "ControlTypeID": ImportField_serializer['ControlType']['id'],
                    "ControlTypeName": ImportField_serializer['ControlType']['Name'],
                    "FieldValidationID": ImportField_serializer['FieldValidation']['id'],
                    "FieldValidationName": ImportField_serializer['FieldValidation']['Name'],
                    "IsCompulsory": ImportField_serializer['IsCompulsory'],
                    "ImportExcelTypeID":ImportField_serializer['ImportExcelType']['id'],
                    "ImportExcelTypeName":ImportField_serializer['ImportExcelType']['Name'],
                    "Format": ImportField_serializer['Format'],
                })
                log_entry = create_transaction_logNew(request, 0, 0,"",397,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ImportField_List[0]})

        except M_ImportFields.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0, 0, "Get single ImportField:"+"ImportField  Not available",7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'ImportField  Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, "Get single ImportField:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        ImportField_data = JSONParser().parse(request)
        try:
            with transaction.atomic(): 
                ImportField_dataByID = M_ImportFields.objects.get(id=id)
                ImportField_serializer = ImportFieldSerializer(ImportField_dataByID, data=ImportField_data)
                if ImportField_serializer.is_valid():
                    ImportFieldID = ImportField_serializer.save()
                    LastInsertID = ImportFieldID.id
                    log_entry = create_transaction_logNew(request, ImportField_data, 0, "",398,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ImportField Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, ImportField_data, 0, "ImportFieldUpdate:"+str(ImportField_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ImportField_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ImportField_data, 0, "ImportFieldUpdate:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                ImportField_data = M_ImportFields.objects.get(id=id)
                ImportField_data.delete()
                log_entry = create_transaction_logNew(request, 0,0,"ImportFieldDeletedID:"+str(id),399,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ImportField Deleted Successfully', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0, 0,"ImportFieldDelete:"+"ImportField used in another table",8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'ImportField used in another table', 'Data': []})

# Party Import Field   Views


class PartyImportFieldFilterView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        PartyImportField_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = PartyImportField_data['PartyID']
                Company = PartyImportField_data['CompanyID']
                IsFieldType = PartyImportField_data['IsFieldType']
                if Party =="":
                    query = M_ImportFields.objects.raw('''SELECT M_ImportFields.id,MC_PartyImportFields.Sequence, M_ImportFields.FieldName, M_ImportFields.IsCompulsory,M_ImportFields.ControlType_id, M_ImportFields.FieldValidation_id,MC_PartyImportFields.Value,MC_PartyImportFields.Party_id,M_ControlTypeMaster.Name ControlTypeName,M_FieldValidations.Name FieldValidationName,M_FieldValidations.RegularExpression,M_ImportFields.Format FROM M_ImportFields Left JOIN MC_PartyImportFields ON M_ImportFields.id = MC_PartyImportFields.ImportField_id JOIN M_ControlTypeMaster ON M_ControlTypeMaster.id = M_ImportFields.ControlType_id JOIN M_FieldValidations ON M_FieldValidations.id = M_ImportFields.FieldValidation_id Where M_ImportFields.ImportExcelType_id = %s ''', ([IsFieldType]))
                    x = 0
                else:    
                    query = M_ImportFields.objects.raw('''SELECT M_ImportFields.id,MC_PartyImportFields.Sequence, M_ImportFields.FieldName, M_ImportFields.IsCompulsory,M_ImportFields.ControlType_id, M_ImportFields.FieldValidation_id,MC_PartyImportFields.Value,MC_PartyImportFields.Party_id,M_ControlTypeMaster.Name ControlTypeName,M_FieldValidations.Name FieldValidationName,M_FieldValidations.RegularExpression,M_ImportFields.Format FROM M_ImportFields Left JOIN MC_PartyImportFields ON M_ImportFields.id = MC_PartyImportFields.ImportField_id AND MC_PartyImportFields.Party_id=%s AND MC_PartyImportFields.Company_id=%s   JOIN M_ControlTypeMaster ON M_ControlTypeMaster.id = M_ImportFields.ControlType_id JOIN M_FieldValidations ON M_FieldValidations.id = M_ImportFields.FieldValidation_id Where M_ImportFields.ImportExcelType_id = %s''', ([Party], [Company],[IsFieldType]))
                    x = Party

                # query= M_ImportFields.objects.prefetch_related('ImportFields').filter(Q(ImportFields__Party=Party) and Q(ImportFields__isnull=False) | Q(ImportFields__isnull=True)  ).values('id','FieldName','IsCompulsory','ControlType_id','FieldValidation_id', 'ImportFields__Value','ImportFields__Party_id')
                # CustomPrint(str(query.query))
                if query:
                    ImportField_serializer = PartyImportFieldSerializerList(
                        query, many=True)
                    log_entry = create_transaction_logNew(request, PartyImportField_data, x, "",400,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ImportField_serializer.data})
                else:
                    log_entry = create_transaction_logNew(request, PartyImportField_data, 0, "No Record Found",7,0)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'No Record Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartyImportField_data, 0, "Party ImportField List:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class PartyImportFieldView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        PartyImportField_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyImport_serializer = PartyImportFieldsSerializer(
                    data=PartyImportField_data, many=True)
                if PartyImport_serializer.is_valid():
                    id = PartyImport_serializer.data[0]['Party']
                    PartyImortField_data = MC_PartyImportFields.objects.filter(
                        Party=id)
                    PartyImortField_data.delete()
                    PartyImport_serializer.save()
                    log_entry = create_transaction_logNew(request, PartyImportField_data, 0, "",401,0,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'PartyImportFields Save Successfully', 'Data': []})
                log_entry = create_transaction_logNew(request, PartyImportField_data, 0, "PartyImportFields Save:"+str(PartyImport_serializer.errors),34,0)
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': PartyImport_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartyImportField_data, 0, "PartyImportFields Save:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        

class ImportExcelTypeView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        ImportExcelType_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ImportExcelType_Serializer = ImportExcelTypeSerializer(data=ImportExcelType_Data)
                if ImportExcelType_Serializer.is_valid():
                    ImportExcelType_Serializer.save()
                    # log_entry = create_transaction_logNew(request, ImportExcelType_Data, 0, "",402,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ImportExcelType Save Successfully', 'Data': []})
                # log_entry = create_transaction_logNew(request, ImportExcelType_Data, 0, "ImportExcelType Save:"+str(ImportExcelType_Serializer.errors),34,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ImportExcelType_Serializer.errors, 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, ImportExcelType_Data, 0, "ImportExcelType Save:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        

class ImportExcelTypeListView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_ImportExcelTypes.objects.all()
                if query:
                    ImportExcelType_Serializer = ImportExcelTypeSerializer(query,many=True).data
                    log_entry = create_transaction_logNew(request, ImportExcelType_Serializer, 0,"",403,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ImportExcelType_Serializer})
                log_entry = create_transaction_logNew(request, 0, 0, "ImportExcelType List:"+"ImportExcelType Not available",7,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'ImportExcelType Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,"ImportExcelType List:"+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})