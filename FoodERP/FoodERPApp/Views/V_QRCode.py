import qrcode
from django.http import HttpResponse
from io import BytesIO
from django.db import transaction
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse

class QRCodeView(CreateAPIView):
        print("=========================Test-1====================================")
        permission_classes = ()        
        print("=========================Test0====================================")
        @transaction.atomic()
        def get(self, request,coupon_code):
            print("=========================Test0.1====================================")
            try:
                with transaction.atomic():   
    
                    print("=========================Test1====================================")
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    print("=========================Test2====================================")
                    qr.add_data(coupon_code)
                    qr.make(fit=True)
                    print("=========================Test3====================================")
                    # Create an image for the QR code
                    img = qr.make_image(fill_color="black", back_color="white")
                    print("=========================Test4====================================")

                    # Save the image in memory as a PNG file
                    buffer = BytesIO()

                    img.save(buffer, format="PNG")
                    # img.save("D:\Pradnya\DeepManthan\qr_code.png", format="PNG")
                    print("=========================Test5====================================")
                    buffer.seek(0)
                    print("=========================Test6====================================")

                    # Return the image as an HTTP response
                    return HttpResponse(buffer, content_type="image/png")
            except Exception as e:
                raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})