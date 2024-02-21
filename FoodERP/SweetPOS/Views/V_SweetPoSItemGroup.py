import base64
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
from FoodERPApp.models import *
from ..Serializer.S_SweetPoSItemGroup import *



class ItemGroupandSubgroupView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        try:
            with transaction.atomic():
                Groups = M_Group.objects.all()
                Grouped_data = []

                for group in Groups:
                    Group_data = {
                        'GroupName': GroupSerializer(group).data,
                        'Subgroups': SubGroupSerializer(group.Group.all(), many=True).data
                    }
                    Grouped_data.append(Group_data)

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Grouped_data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
