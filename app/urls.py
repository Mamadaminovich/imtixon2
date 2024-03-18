from django.urls import path
from .views import *

urlpatterns = [
    path('webhook/', WebhookView.as_view(), name='webhook'),
]