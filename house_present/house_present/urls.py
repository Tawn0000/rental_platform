"""house_present URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path
# from . import view
from house.views import House_view
from house import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', House_view.index, name='index'),
    re_path(r'^rent', House_view.rent, name='rent'),
    re_path(r'^predict/$', House_view.predict, name='predict'),
    re_path(r'^feedback/$', House_view.feedback, name='feedback'),
]
