# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""mofa URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('assistants/', include('assistants.urls')),
    path('', admin.site.urls),
    path('chaining/', include('smart_selects.urls')),
    path('analytics/', include('analytics.urls')),
    path('db/', include('database_API.urls')),
]

admin.site.site_header = "Mofa Admin"
admin.site.site_title = "Mofa Admin Portal"
admin.site.index_title = "Welcome to the Mofa Portal"
