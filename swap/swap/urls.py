"""
URL configuration for swap project.

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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
    path('', views.index, name='index'),
    path('agent_verification', views.agent_verification, name='agent_verification'),
    path('agent_administratif', views.agent_administratif, name='agent_administratif'),
    path('agent_technique', views.agent_technique, name='agent_technique'),
    path('agent_technique_pro', views.agent_technique_pro, name='agent_technique_pro'),
    path('agent_moteur', views.agent_moteur, name='agent_moteur'),
    path('agent_hors_garantie', views.agent_hors_garantie, name='agent_hors_garantie'),
    path('agent_entrepot', views.agent_entrepot, name='agent_entrepot'),
    path('agent_station', views.agent_station, name='agent_station'),
    path('agent_pieces', views.agent_pieces, name='agent_pieces'),
    path('other_admins', views.other_admins, name='other_admins'),
    path('simple_tickets', views.simple_tickets, name='simple_tickets'),
    path('tickets_hivernage', views.tickets_hivernage, name='tickets_hivernage'),
    path('ru_shower', views.ru_shower, name='ru_shower'),
    path('login/', views.log_in, name='login'),
]
