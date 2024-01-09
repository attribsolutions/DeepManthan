from django.urls import re_path as url ,path

from FoodERPApp.Views.V_abc import AbcView

urlpatterns = [
    
    # Master APIs IN Projects Add Page ,List Page
    url(r'test', AbcView.as_view()),
]