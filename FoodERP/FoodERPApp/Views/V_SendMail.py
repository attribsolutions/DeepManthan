from ast import Not
from genericpath import exists
import random
from urllib import response
from django.conf import settings
from django.urls import is_valid_path
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.core.mail import send_mail
from ..helpers import send_otp_to_phone

from ..models import *

from ..Serializer.S_SendMail import *


class SendViewMail(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Email = request.data.get('Email')
        phone = request.data.get('Phone')
        if Email:
            Employee = M_Employees.objects.filter(
                email__exact=str(Email)).values('id', 'Name')
            # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data': str(Employee) })
            if Employee.exists():
                Employeedata_Serializer = Employeeserializer(
                    Employee, many=True).data
                # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' :Employeedata_Serializer[0]['id']})
                userquery = M_Users.objects.filter(
                    Employee=Employeedata_Serializer[0]['id']).values('id', 'LoginName')
                # return JsonResponse({'StatusCode': 406, 'Status': True,'Data' :user})
                if userquery.exists():
                    Usersdata_Serializer = Userserializer(
                        userquery, many=True).data
                    LoginName = Usersdata_Serializer[0]['LoginName']

                    otp = random.randint(1000, 9999)
                    userOTP = M_Users.objects.filter(
                        Employee=Employeedata_Serializer[0]['id']).update(OTP=otp)
                    subject = 'Your Account Verification mail'
                    newline = '\n'
                    message = f'''Your Login Name: {LoginName} {newline}Your OTP is {otp} '''
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [Email]
                    send_mail(subject, message, email_from, recipient_list)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Mail send Successfully', 'Data': []})
                else:
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Please check Mail And Phone', 'Data': []})
            else: 
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Please check Mail And Phone', 'Data': []})   
        else:
            PhoneNo = str(phone)
            Employee = M_Employees.objects.filter(
                Mobile__exact=PhoneNo).values('id', 'Name')
            # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': '111111111', 'Data' :str(Employee.query)})
            if Employee.exists():
                Employeedata_Serializer = Employeeserializer(
                    Employee, many=True).data
                # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' :Employeedata_Serializer[0]['id']})
                userquery = M_Users.objects.filter(
                    Employee=Employeedata_Serializer[0]['id']).values('id', 'LoginName')
                # return JsonResponse({'StatusCode': 406, 'Status': True,'Data' :str(userquery.query)})
                if userquery.exists():
                    Usersdata_Serializer = Userserializer(
                        userquery, many=True).data
                    LoginName = Usersdata_Serializer[0]['LoginName']
                    otp = random.randint(1000, 9999)
                    userOTP = M_Users.objects.filter(
                        Employee=Employeedata_Serializer[0]['id']).update(OTP=otp)
                    send_otp_to_phone(otp, PhoneNo)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data': otp})
                    # subject = 'Your Account Verification mail'
                    # newline = '\n'
                    # message = f'''Your Login Name: {LoginName} {newline}Your OTP is {otp} '''
                    # email_from = settings.EMAIL_HOST_USER
                    # recipient_list= [email]
                    # send_mail(subject , message , email_from , recipient_list)
                    # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' : []})

        # subject = 'Your Account Verification mail'
        # otp = random.randint(1000, 9999)
        # message = f'Your OTP is {otp} '
        # email_from = settings.EMAIL_HOST_USER
        # recipient_list= ['pradnyaubale12@gmail.com','hemantwaghmare13@gmail.com']
        # send_mail(subject , message , email_from , recipient_list)
        # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' : []})


class VerifyOTPwithUserData(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                LoginName = request.data.get("LoginName")
                verifyOTP = request.data.get('OTP')
                if LoginName and verifyOTP:
                    User = M_Users.objects.filter(LoginName__exact=str(LoginName)).filter(
                        OTP__exact=str(verifyOTP)).values('id', 'LoginName')
                    if User.exists():
                        Userdata_Serializer = Userserializer(
                            User, many=True).data
                        userOTP = M_Users.objects.filter(
                            id=Userdata_Serializer[0]['id']).update(OTP=None)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'LoginName And  OTP Match Successfully... ', 'Data': []})
                    else:
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Please Enter Correct Login Name and OTP..', 'Data': []})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Please Enter Correct Login Name and OTP..', 'Data': []})
        except:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': '', 'Data': []})
