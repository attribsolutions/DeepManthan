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

class ImportFieldSaveView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ImportField_data = JSONParser().parse(request)
                ImportField_serializer = ImportField_Serializer(data=ImportField_data)
                if ImportField_serializer.is_valid():
                   ImportField_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ImportField Save Successfully', 'Data': []})
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ImportField_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
class PartyImportFieldFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartyImportField_data = JSONParser().parse(request)
                Party = PartyImportField_data['PartyID']
                CompanyID = PartyImportField_data['CompanyID'] 
                query = M_ImportFields.objects.raw('''SELECT m_importfields.id, m_importfields.FieldName, m_importfields.IsCompulsory,m_importfields.ControlType_id, m_importfields.FieldValidation_id,mc_partyimportfields.Value,m_controltypemaster.Name ControlTypeName,m_fieldvalidations.Name FieldValidationName FROM m_importfields Left JOIN mc_partyimportfields ON m_importfields.id = mc_partyimportfields.ImportField_id AND mc_partyimportfields.Party_id=%s  JOIN m_controltypemaster ON m_controltypemaster.id = m_importfields.ControlType_id JOIN m_fieldvalidations ON m_fieldvalidations.id = m_importfields.FieldValidation_id''',([Party]))
                # query = M_ImportFields.objects.filter(Q(ImportFields__isnull=True)).values('id','FieldName','IsCompulsory','ControlType', 'FieldValidation','ImportFields__Value','ImportFields__Party_id')
                # print(str(query.query))
                if query:
                    ImportField_serializer = PartyImportFieldSerializerList(query, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ImportField_serializer.data})
                else:
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ImportField_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        
        