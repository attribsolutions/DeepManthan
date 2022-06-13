from rest_framework.views import exception_handler
from rest_framework.response import Response

def CustomException(exc,context):
    response = exception_handler(exc, context)
    
    print(exc)
    exc_list = str(exc).split("Detail")
   
    return Response({"StatusCode":403,"Status":'true',"ErrorMessage":exc_list[0]},status=403)