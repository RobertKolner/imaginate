from django.conf.urls import patterns, include, url
from views import IndexView, CacheView

urlpatterns = patterns('',
    url(r'^image/(?P<url>.*)$', IndexView.as_view(), name='home'),
    url(r'^cache/$', CacheView.as_view(), name='cache'),
)
