from django.urls import re_path as url ,path

from .Views.V_SweetPosRoleAccess import *

from .Views.V_SweetPoSItemGroup import *


urlpatterns = [
    
    # Master APIs IN Projects Add Page ,List Page
    url(r'SPOSroleaccess$', SweetPosRoleAccessView.as_view()),
    url(r'Lspos$', SPOSLog_inView.as_view()),
    url(r'ItemGroupandSubgroup$', ItemGroupandSubgroupView.as_view()),
    url(r'ItemList$', ItemListView.as_view())
        
    
    
    
    
]