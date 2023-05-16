from django.http import JsonResponse
def custom404(request, exception=None):
    return JsonResponse({
        'StatusCode': 404,
        'Status' : True,
        'Message': 'Page not found',
        'Data':[]
    })

def custom500(request, exception=None):
    return JsonResponse({
        'StatusCode': 500,
        'Status' : True,
        'Message':'Internal Server Error',
        'Data':[]
    }) 

 