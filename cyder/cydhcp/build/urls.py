from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.build.views import build_network


urlpatterns = patterns(
    '',
    url(r'(?P<network_pk>[\w-]+)/$', build_network, name='build-network'),
)
