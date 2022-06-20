from django.http import JsonResponse

def custom404(request, exception=None):
    return JsonResponse({
        'status_code': 404,
        'status' : True,
        'Error': 'Page not found'
    })

def custom500(request, exception=None):
    return JsonResponse({
        'status_code': 500,
        'status' : True,
        'Error':'Internal Server Error'
    }) 

 