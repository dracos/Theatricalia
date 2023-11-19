from django.urls import path
from lp import views


urlpatterns = [
    path('edition/', views.edition),
    path('sample/', views.sample),
    path('meta.json', views.meta_json),
    path('icon.png', views.icon),
]
