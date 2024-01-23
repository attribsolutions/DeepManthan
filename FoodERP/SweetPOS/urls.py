from django.urls import re_path as url ,path

from .views import SPOSRoleAccess

urlpatterns = [
    
    # Master APIs IN Projects Add Page ,List Page
    url(r'SPOSroleaccess$', SPOSRoleAccess.as_view()),
    
    
]