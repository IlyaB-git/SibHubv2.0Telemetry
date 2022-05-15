from django.urls import path
from .views import *

urlpatterns = [
    path('', select_per, name='select_per'),
    path('per/<str:id_cofe>/<int:from_time>/<int:to_time>/', period, name='period'),
    path('login/', user_login, name='login'),
    path('load/', loader_db, name='load'),
    path('logout/', logout_view, name='logout'),
    path('video/<str:video_pk>', get_streaming_video, name='video')
]
