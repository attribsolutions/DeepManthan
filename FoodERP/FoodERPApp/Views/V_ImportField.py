# from ..models import *
# from ..Serializer.S_BankMaster import *
# from django.http import JsonResponse
# from rest_framework.generics import CreateAPIView
# from rest_framework.permissions import IsAuthenticated
# # from rest_framework_jwt.authentication import JSONWebTokenAuthentication
# from django.db import IntegrityError, transaction
# from rest_framework.parsers import JSONParser
# from ..Serializer.S_ImportField import *
# from django.db.models import Q

# class ImportFieldSaveView(CreateAPIView):

#     permission_classes = (IsAuthenticated,)
#     # authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 ImportField_data = JSONParser().parse(request)
#                 ImportField_serializer = ImportField_Serializer(data=ImportField_data)
#                 if ImportField_serializer.is_valid():
#                    ImportField_serializer.save()
#                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ImportField Save Successfully', 'Data': []})
#             return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ImportField_serializer.errors, 'Data': []})
#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
# class PartyImportFieldFilterView(CreateAPIView):
    
#     permission_classes = (IsAuthenticated,)
#     # authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 PartyImportField_data = JSONParser().parse(request)
#                 Party = PartyImportField_data['PartyID']
#                 Company = PartyImportField_data['CompanyID'] 
#                 query = M_ImportFields.objects.raw('''SELECT M_ImportFields.id, M_ImportFields.FieldName, M_ImportFields.IsCompulsory,M_ImportFields.ControlType_id, M_ImportFields.FieldValidation_id,MC_PartyImportFields.Value,MC_PartyImportFields.Party_id,M_ControlTypeMaster.Name ControlTypeName,M_FieldValidations.Name FieldValidationName FROM M_ImportFields Left JOIN MC_PartyImportFields ON M_ImportFields.id = MC_PartyImportFields.ImportField_id AND MC_PartyImportFields.Party_id=%s AND MC_PartyImportFields.Company_id=%s   JOIN m_controltypemaster ON m_controltypemaster.id = M_ImportFields.ControlType_id JOIN M_FieldValidations ON M_FieldValidations.id = M_ImportFields.FieldValidation_id''',([Party],[Company]))
             
#                 # query= M_ImportFields.objects.prefetch_related('ImportFields').filter(Q(ImportFields__Party=Party) and Q(ImportFields__isnull=False) | Q(ImportFields__isnull=True)  ).values('id','FieldName','IsCompulsory','ControlType_id','FieldValidation_id', 'ImportFields__Value','ImportFields__Party_id')
#                 # print(str(query.query))                                                             
#                 if query:
#                     ImportField_serializer = PartyImportFieldSerializerList(query, many=True)
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ImportField_serializer.data})
#                 else:
#                     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ImportField_serializer.errors, 'Data': []})
#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(query.query), 'Data': str(query.query)})
        
# class PartyImportFieldView(CreateAPIView):
    
#     permission_classes = (IsAuthenticated,)
#     # authentication_class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 PartyImportField_data = JSONParser().parse(request)
#                 PartyImport_serializer = PartyImportFieldsSerializer(data=PartyImportField_data, many=True)
#                 if PartyImport_serializer.is_valid():
#                     id = PartyImport_serializer.data[0]['Party']
#                     PartyImortField_data = MC_PartyImportFields.objects.filter(Party=id)
#                     PartyImortField_data.delete()
#                     PartyImport_serializer.save()
#                     return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'PartyImportFields Save Successfully', 'Data': []})
#                 return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': PartyImport_serializer.errors, 'Data': []})
#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                
                
        