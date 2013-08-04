from django.conf.urls import patterns, url


urlpatterns = patterns('',

    url(r'^edition/$', 'lp.views.edition'),
    url(r'^sample/$', 'lp.views.sample'),
    url(r'^meta.json$', 'lp.views.meta_json'),
    url(r'^icon.png$', 'lp.views.icon'),
    
)




