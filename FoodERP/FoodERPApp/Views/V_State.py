from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_State import *

from ..models import *

class S_StateView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_Statedata = M_State.objects.all()
                M_State_serializer =  StateSerializer(M_Statedata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_State_serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                M_Statedata = JSONParser().parse(request)
                M_State_serializer = StateSerializer(data=M_Statedata)
                if M_State_serializer.is_valid():
                    M_State_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Save Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  M_State_serializer.errors})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e)})
            print(e)        
