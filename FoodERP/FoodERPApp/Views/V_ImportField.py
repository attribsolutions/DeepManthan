from ..models import *
from ..Serializer.S_BankMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_ImportField import *

class ImportFieldSaveView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ImportField_data = JSONParser().parse(request)
                PartyImportField_serializer = ImportField_Serializer(data=ImportField_data)
                if PartyImportField_serializer.is_valid():
                   PartyImportField_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ImportField Save Successfully', 'Data': []})
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyImportField_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})