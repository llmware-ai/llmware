"""
URL configuration for Judica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from Judica.views import *
from User_Profile.views import *
from AI_courtroom.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('file-case/',file_case, name='file_case'),
    path('cases/',user_cases, name='user_cases'),
    path('messages/',user_messages, name='user_messages'),
    path('courtroom/<int:case_id>/', courtroom_view, name='courtroom_view'),
    path('courtroom/<int:case_id>/send_message/', send_message, name='send_message'),
    path('verdict/<int:courtroom_id>/', verdict_view, name='verdict_view')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
