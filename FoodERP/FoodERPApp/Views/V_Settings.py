from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Settings import *
from ..models import *


class SettingsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request ):
        try:
            with transaction.atomic():
                Settings_data = JSONParser().parse(request)
                Settings_data_serializer = SettingsSerializer(data= Settings_data)
                if  Settings_data_serializer.is_valid():
                    Settings_data_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' Settings Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Settings_data_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
