from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_TermsAndConditions import *
from ..models import  *

class TermsAndCondtionsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication  

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                TermsCondition = JSONParser().parse(request)
                TermsCondition_serializer = M_TermsAndConditionsSerializer(data=TermsCondition)
                if TermsCondition_serializer.is_valid():
                    TermsCondition_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'TermsAndCondtions Save Successfully' , 'Data':[] })
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': TermsCondition_serializer.errors , 'Data':[]})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})   

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                TermsCondition = M_TermsAndConditions.objects.all()
                if TermsCondition.exists():
                    TermsCondition_serializer = M_TermsAndConditionsSerializer(
                    TermsCondition, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': TermsCondition_serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'TermsAndConditions Not available', 'Data': []})    
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class TermsAndCondtionsViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                TermsConditiondata = M_TermsAndConditions.objects.get(id=id)
                TermsConditiondata_serializer = M_TermsAndConditionsSerializer(TermsConditiondata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': TermsConditiondata_serializer.data})
        except  M_TermsAndConditions.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'TermsAndConditions Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                TermsConditiondata = JSONParser().parse(request)
                TermsConditiondataByID = M_TermsAndConditions.objects.get(id=id)
                TermsCondition_serializer = M_TermsAndConditionsSerializer(
                    TermsConditiondataByID, data=TermsConditiondata)
                if TermsCondition_serializer.is_valid():
                    TermsCondition_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'TermsAndConditions Type Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': TermsCondition_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                TermsConditiondata = M_TermsAndConditions.objects.get(id=id)
                TermsConditiondata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'TermsAndConditions  Deleted Successfully','Data':[]})
        except M_TermsAndConditions.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'TermsAndConditions  Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'TermsAndConditions  used in another table', 'Data': []})            