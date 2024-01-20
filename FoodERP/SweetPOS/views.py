from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
# Create your views here.

class SPOSRoleAccess(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                # RoleAccess_data = JSONParser().parse(request)
                print('ddddddddddddddddddddddddd')
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'hiiiiiiiiiiiiiiiiiiii', 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})