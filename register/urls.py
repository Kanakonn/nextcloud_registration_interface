"""nextcloud_register URL Configuration
"""
from django.urls import path

from register.views import RegisterView, GenerateInvitesView

urlpatterns = [
    path('generate', GenerateInvitesView.as_view(), name='generate'),
    path('', RegisterView.as_view(), name='register'),
]
