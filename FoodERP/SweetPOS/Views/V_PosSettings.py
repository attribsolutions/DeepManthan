from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import M_PosSettings
from ..Serializer.S_PosSettings import *
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse

class PosSettings(APIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            with transaction.atomic():
                settings = M_PosSettings.objects.all()
                serializer = M_PosSettingsListSerializer(settings, many=True)
                return JsonResponse({
                    "StatusCode": 200,
                    "Status": True,
                    "Message": "Settings fetched successfully",
                    "Data": serializer.data
                }, status=200)
        except Exception as e:
            return JsonResponse({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e),
                "Data": []
            }, status=500)

    def post(self, request):
        try:
            with transaction.atomic():
                serializer = M_PosSettingsCreateUpdateSerializer(data=request.data)
                if serializer.is_valid():
                    setting = serializer.save()
                    return JsonResponse({
                        "StatusCode": 200,
                        "Status": True,
                        "Message": "Setting created successfully",
                        "Data": {"SettingID": setting.id}
                    }, status=201)
                return JsonResponse({
                    "StatusCode": 400,
                    "Status": False,
                    "Message": "Validation errors",
                    "Data": serializer.errors
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e),
                "Data": []
            }, status=500)



class PosSettingsDetail(APIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            setting = M_PosSettings.objects.get(id=pk)
            serializer = M_PosSettingsListSerializer(setting)
            return JsonResponse({
                "StatusCode": 200,
                "Status": True,
                "Message": "Setting retrieved successfully",
                "Data": serializer.data
                }, status=200)
        except M_PosSettings.DoesNotExist:
            return JsonResponse({
                "StatusCode": 404,
                "Status": False,
                "Message": "Setting not found",
                "Data": []
            }, status=404)
        except Exception as e:
            return JsonResponse({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e),
                "Data": []
            }, status=500)

    def put(self, request, pk):
        try:
            with transaction.atomic():
                setting = M_PosSettings.objects.get(id=pk)
                serializer = M_PosSettingsCreateUpdateSerializer(setting, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({
                            "StatusCode": 200,
                            "Status": True,
                            "Message": "Setting updated successfully",
                            "Data": []
                        }, status=200)

                return JsonResponse({
                    "StatusCode": 400,
                    "Status": False,
                    "Message": "Validation errors",
                    "Data": serializer.errors
                }, status=400)
        except M_PosSettings.DoesNotExist:
            return JsonResponse({
                "StatusCode": 404,
                "Status": False,
                "Message": "Setting not found",
                "Data": []
            }, status=404)
        except Exception as e:
            return JsonResponse({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e),
                "Data": []
            }, status=500)

    def delete(self, request, pk):
        try:
            with transaction.atomic():
                setting = M_PosSettings.objects.get(id=pk)
                setting.delete()
                return JsonResponse({
                    "StatusCode": 200,
                    "Status": True,
                    "Message": "Setting deleted successfully",
                    "Data": []
                }, status=200)
        except M_PosSettings.DoesNotExist:
            return JsonResponse({
                "StatusCode": 404,
                "Status": False,
                "Message": "Setting not found",
                "Data": []
            }, status=404)
        except Exception as e:
            return JsonResponse({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e),
                "Data": []
            }, status=500)
