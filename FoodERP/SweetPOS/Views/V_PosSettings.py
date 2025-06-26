from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import M_PosSettings
from ..Serializer.S_PosSettings import *
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class PosSettings(APIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            with transaction.atomic():
                settings = M_PosSettings.objects.all()
                serializer = M_PosSettingsListSerializer(settings, many=True)
                return Response({
                    "StatusCode": 200,
                    "Status": True,
                    "Data": serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            with transaction.atomic():
                serializer = M_PosSettingsCreateUpdateSerializer(data=request.data)
                if serializer.is_valid():
                    setting = serializer.save()
                    return Response({
                        "StatusCode": 200,
                        "Status": True,
                        "Message": "Setting created successfully",
                        "SettingID": setting.id
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "StatusCode": 400,
                    "Status": False,
                    "Errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PosSettingsDetail(APIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            setting = M_PosSettings.objects.get(id=pk)
            serializer = M_PosSettingsListSerializer(setting)
            return Response({
                "StatusCode": 200,
                "Status": True,
                "Data": serializer.data
            }, status=status.HTTP_200_OK)
        except M_PosSettings.DoesNotExist:
            return Response({
                "StatusCode": 404,
                "Status": False,
                "Message": "Setting not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            with transaction.atomic():
                setting = M_PosSettings.objects.get(id=pk)
                serializer = M_PosSettingsCreateUpdateSerializer(setting, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "StatusCode": 200,
                        "Status": True,
                        "Message": "Setting updated successfully"
                    }, status=status.HTTP_200_OK)

                return Response({
                    "StatusCode": 400,
                    "Status": False,
                    "Errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except M_PosSettings.DoesNotExist:
            return Response({
                "StatusCode": 404,
                "Status": False,
                "Message": "Setting not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            with transaction.atomic():
                setting = M_PosSettings.objects.get(id=pk)
                setting.delete()
                return Response({
                    "StatusCode": 200,
                    "Status": True,
                    "Message": "Setting deleted successfully"
                }, status=status.HTTP_200_OK)
        except M_PosSettings.DoesNotExist:
            return Response({
                "StatusCode": 404,
                "Status": False,
                "Message": "Setting not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
