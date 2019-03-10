from django.conf.urls import url
from lp import views


urlpatterns = [
    url(r'^edition/$', views.edition),
    url(r'^sample/$', views.sample),
    url(r'^meta.json$', views.meta_json),
    url(r'^icon.png$', views.icon),
]
