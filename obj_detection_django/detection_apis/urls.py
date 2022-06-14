from django.urls import path
from . import views
urlpatterns = [
    path('link/', views.DetectionLink.as_view(), name='by-link'),
    path('file/', views.DetectionFile.as_view(), name='by-file'),
    # path('link/<str:link>/', views.Detection.as_view(), name='by-link'),

]