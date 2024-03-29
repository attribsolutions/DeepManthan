"""FoodERP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from FoodERPApp.Views.V_Errorhandler import *
from django.conf import settings

urlpatterns = [
#    path('admin/', admin.site.urls),
    path('', include('FoodERPApp.urls')),
    path('SweetPOS/', include('SweetPOS.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 =  'FoodERPApp.Views.V_Errorhandler.custom404'
handler500 =  'FoodERPApp.Views.V_Errorhandler.custom500'
 