from django.urls import re_path as url ,path

from .Views.V_SweetPosRoleAccess import *

urlpatterns = [
    
    # Master APIs IN Projects Add Page ,List Page
    url(r'SPOSroleaccess$', SweetPosRoleAccessView.as_view()),
    
    url(r'SPOSroleaccess/([0-9]+)$', SPosRoleAccessUpdateView.as_view()),
    
    
]