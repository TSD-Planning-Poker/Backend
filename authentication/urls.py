"""PlanningPoker URL Configuration

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
# from xml.etree.ElementInclude import include
from django.urls import include, path
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken import views
from .views import logout_view, ProfileApiView

urlpatterns = [
    path('login/', views.obtain_auth_token, name="log_in"),
    path('logout/', logout_view, name="log_out"),
    path('profile/', ProfileApiView.as_view(), name="profile")
]
