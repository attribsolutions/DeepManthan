from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import M_PosSettings
from ..Serializer.S_PosSettings import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.db import transaction
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction
from rest_framework.parsers import JSONParser


class PosSettings(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        try:
            with transaction.atomic():
                user = BasicAuthenticationfunction(request)

                if user is not None:
                    settings = M_PosSettings.objects.filter(Is_Disabled=False)
                    serializer = M_PosSettingsListSerializer(settings, many=True)
                    return Response({
                        "StatusCode": 200,
                        "Status": True,
                        "Data": serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "StatusCode": 401,
                    "Status": False,
                    "Message": "Unauthorized"
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            with transaction.atomic():
                user = BasicAuthenticationfunction(request)
                if user is None:
                    return Response({
                        "StatusCode": 6001,
                        "Status": False,
                        "Message": "Unauthorized"
                    }, status=status.HTTP_401_UNAUTHORIZED)

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
    
    def put(self, request, pk=None):
        try:
            print("id=",pk)
            with transaction.atomic():
                user = BasicAuthenticationfunction(request)
                if user is None:
                    return Response({
                        "StatusCode": 401,
                        "Status": False,
                        "Message": "Unauthorized"
                    }, status=status.HTTP_401_UNAUTHORIZED)

                if not pk:
                    return Response({
                        "StatusCode": 400,
                        "Status": False,
                        "Message": "Setting ID is required for update"
                    }, status=status.HTTP_400_BAD_REQUEST)

                try:
                    setting = M_PosSettings.objects.get(id=pk)
                except M_PosSettings.DoesNotExist:
                    return Response({
                        "StatusCode": 404,
                        "Status": False,
                        "Message": "Setting not found"
                    }, status=status.HTTP_404_NOT_FOUND)

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

        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk=None):
        try:
            with transaction.atomic():
                user = BasicAuthenticationfunction(request)
                if user is None:
                    return Response({
                        "StatusCode": 401,
                        "Status": False,
                        "Message": "Unauthorized"
                    }, status=status.HTTP_401_UNAUTHORIZED)

                if not pk:
                    return Response({
                        "StatusCode": 400,
                        "Status": False,
                        "Message": "Setting ID is required for delete"
                    }, status=status.HTTP_400_BAD_REQUEST)

                try:
                    setting = M_PosSettings.objects.get(id=pk)
                except M_PosSettings.DoesNotExist:
                    return Response({
                        "StatusCode": 404,
                        "Status": False,
                        "Message": "Setting not found"
                    }, status=status.HTTP_404_NOT_FOUND)

                setting.delete()
                return Response({
                    "StatusCode": 200,
                    "Status": True,
                    "Message": "Setting deleted successfully"
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)