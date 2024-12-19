import qrcode
from django.http import HttpResponse
from io import BytesIO
from django.db import transaction
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse

class QRCodeView(CreateAPIView):
        
        permission_classes = ()
        

        @transaction.atomic()
        def get(self, request,coupon_code):
            try:
                with transaction.atomic():   
    
    
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(coupon_code)
                    qr.make(fit=True)

                    # Create an image for the QR code
                    img = qr.make_image(fill_color="black", back_color="white")

                    # Save the image in memory as a PNG file
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)

                    # Return the image as an HTTP response
                    return HttpResponse(buffer, content_type="image/png")
            except Exception as e:
                raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})