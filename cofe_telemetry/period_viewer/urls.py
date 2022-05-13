from django.urls import path
from .views import *

urlpatterns = [
    path('', select_per),
    path('per/<str:id_cofe>/<int:from_time>/<int:to_time>/', period),
    path('login/', login),
    path('video/', videoplayer)
]
