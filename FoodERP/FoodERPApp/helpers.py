import requests
from django.test import Client

def send_otp_to_phone(PhoneNo,message):
        try:
            link='http://api.msg91.com/api/sendhttp.php?route=4&sender=PUROHT&mobiles={PhoneNo}&authkey=267833AY89X9mps5c8cd925&message={message}' 
            result = requests.get(link, verify=False)
            return
        except Exception as e:
            return None

    









# from django.conf import settings

# def send_otp_to_phone(otp,PhoneNo):
#     try:
#         # ID = 'vishvas.chitale@gmail.com'
# 	    # Pwd = 'pass1234'
# 		url = f'http://SMSnMMS.co.in/smsaspx?ID=vishvas.chitale@gmail.com&Pwd=pass1234&PhNo={PhoneNo}&Text={otp}'
       
    
#     except Exception as e:
#         return None

#  client = Client(account_sid, auth_token)

#     message = client.messages.create(
#         to="7887520002", 
#         from_="8625008710",
#         body="Hello from Python!")
