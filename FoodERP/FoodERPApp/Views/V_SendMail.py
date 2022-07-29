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
    def get(self, request):
        Email = request.data.get('Email')
        phone = request.data.get('Phone')
        if Email:
            email  = str(Email)
            Employee = M_Employees.objects.filter(email__exact = email).values('id','Name')
            
            if Employee.exists():
                Employeedata_Serializer = Employeeserializer(Employee, many=True).data
                # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' :Employeedata_Serializer[0]['id']})
                userquery = M_Users.objects.filter(Employee = Employeedata_Serializer[0]['id']).values('id','LoginName')
                # return JsonResponse({'StatusCode': 406, 'Status': True,'Data' :user})
                if userquery.exists():
                    Usersdata_Serializer = Userserializer(userquery, many=True).data
                    LoginName = Usersdata_Serializer[0]['LoginName']
                    
                    otp = random.randint(1000, 9999)
                    userOTP = M_Users.objects.filter(Employee = Employeedata_Serializer[0]['id']).update(OTP=otp)
                    subject = 'Your Account Verification mail'
                    newline = '\n'
                    message = f'''Your Login Name: {LoginName} {newline}Your OTP is {otp} '''
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list= [email]
                    send_mail(subject , message , email_from , recipient_list)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' : []})
        else:
            PhoneNo  = str(phone)
            Employee = M_Employees.objects.filter(Mobile__exact = PhoneNo).values('id','Name')
            # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': '111111111', 'Data' :str(Employee.query)})
            if Employee.exists():
                Employeedata_Serializer = Employeeserializer(Employee, many=True).data
                # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' :Employeedata_Serializer[0]['id']})
                userquery = M_Users.objects.filter(Employee = Employeedata_Serializer[0]['id']).values('id','LoginName')
                # return JsonResponse({'StatusCode': 406, 'Status': True,'Data' :str(userquery.query)})
                if userquery.exists():
                    Usersdata_Serializer = Userserializer(userquery, many=True).data
                    LoginName = Usersdata_Serializer[0]['LoginName']
                    otp = random.randint(1000, 9999)
                    userOTP = M_Users.objects.filter(Employee = Employeedata_Serializer[0]['id']).update(OTP=otp)
                    send_otp_to_phone(otp,PhoneNo)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mail send Successfully', 'Data' : otp})
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
    
    
    