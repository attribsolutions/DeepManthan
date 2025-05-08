import base64
import hashlib
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *


from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.db import transaction



class PhonePayReceiveMsg(APIView):
    permission_classes = []  # Disable auth checks if this is a public endpoint

    @transaction.atomic
    def post(self, request):
        try:
            header = JSONParser().parse(request)
            return phonepe_callback(request, header)

        except Exception as exc:
            # create_transaction_logNew(request, 0, 0, 'FileUploadedError: ' + str(exc), 33, 0)
            return JsonResponse({
                'StatusCode': 400,
                'Status': False,
                'Message': str(exc),
                'Data': []
            })

# Callback Handler
def phonepe_callback(request, body_data):
    try:
        SALT_KEY = 'dummy_salt_key_for_testing'
        SALT_INDEX = '1'
        # print('*****')
        x_verify_header = request.headers.get('x-verify')
        base64_response = body_data.get('response')
        # print(base64_response)
        if not base64_response:
            return JsonResponse({'error': 'Missing response'}, status=400)

        # Step 2: Validate signature
        computed_hash = hashlib.sha256((base64_response + SALT_KEY).encode()).hexdigest()
        # print(computed_hash)
        expected_x_verify = f"{computed_hash}###{SALT_INDEX}"
        # print(expected_x_verify)

        if x_verify_header != expected_x_verify:
            return JsonResponse({'error': 'Invalid signature'}, status=403)

        # Step 3: Decode base64 response
        decoded_response = base64.b64decode(base64_response).decode('utf-8')
        # print(decoded_response,"*****")
        response_data = json.loads(decoded_response)
        # print(response_data,"************")
        code = response_data.get("code")
        transaction_data = response_data.get("data", {})
        transaction_id = transaction_data.get("transactionId")
        amount = transaction_data.get("amount")
        payment_state = transaction_data.get("paymentState")

        # Step 4: Handle payment status
        if code == "PAYMENT_SUCCESS":
            print(f"Payment Success: {transaction_id}, Amount: {amount}")
        elif code == "PAYMENT_ERROR":
            print(f"Payment Failed: {transaction_id}")
        elif code == "PAYMENT_CANCELLED":
            print(f"Payment Cancelled: {transaction_id}")
        else:
            print(f"Unknown status: {code}")

        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Payment callback processed.'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)







