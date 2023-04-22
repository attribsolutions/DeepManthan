

from ..models import *
from ..Serializer.S_MappingMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser


class PartyCustomerMappingView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self,request):
        try:
            with transaction.atomic():
                PartyCustomerMappingMaster_data = JSONParser().parse(request)
                PartyCustomerMapping_Serializer = PartyMasterMappingSerializer(data=PartyCustomerMappingMaster_data,many=True)
                if PartyCustomerMapping_Serializer.is_valid():
                    id = PartyCustomerMapping_Serializer.data[0]['Party']
                    Partycustomerdata = M_PartyCustomerMappingMaster.objects.filter(Party=id)
                    Partycustomerdata.delete()
                    PartyCustomerMapping_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyMaster Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PartyCustomerMapping_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_PartySubParty.objects.raw('''SELECT MC_PartySubParty.id,M_Parties.Name as CustomerName ,MC_PartySubParty.Party_id,MC_PartySubParty.SubParty_id as Customer,M_PartyCustomerMappingMaster.MapCustomer From MC_PartySubParty LEFT join M_PartyCustomerMappingMaster ON M_PartyCustomerMappingMaster.Customer_id = MC_PartySubParty.SubParty_id JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id AND MC_PartySubParty.Party_id=%s''', ([id]))
                if query:
                    Party_Serializer = PartyCustomerMappingSerializerSecond(query,many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Party_Serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Party not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
