

# from twilio.rest import Client

from django.test import Client


def send_otp_to_phone(otp,PhoneNo):

    # Your Account SID from twilio.com/console
    account_sid = "AC1a70610ba0f48ed102b2250b8359bb69"
    # Your Auth Token from twilio.com/console
    auth_token  = "479e20689110950f72366edfc0b3d025"

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="7887520002", 
        from_="8625008710",
        body="Hello from Python!")
    









# from django.conf import settings

# def send_otp_to_phone(otp,PhoneNo):
#     try:
#         # ID = 'vishvas.chitale@gmail.com'
# 	    # Pwd = 'pass1234'
# 		url = f'http://SMSnMMS.co.in/smsaspx?ID=vishvas.chitale@gmail.com&Pwd=pass1234&PhNo={PhoneNo}&Text={otp}'
       
    
#     except Exception as e:
#         return None


