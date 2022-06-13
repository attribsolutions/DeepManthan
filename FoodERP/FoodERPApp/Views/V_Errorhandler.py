from django.http import JsonResponse

def custom404(request, exception=None):
    return JsonResponse({
        'status_code': 404,
        'Error': 'Page not found'
    })

def custom500(request, exception=None):
    return JsonResponse({
        'status_code': 500,
        'Error':'Internal Server Error'
    }) 