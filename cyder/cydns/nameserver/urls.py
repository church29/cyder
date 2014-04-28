from django.conf.urls.defaults import patterns, url

from cyder.cydns.nameserver.views import create_ns_delegated, NSCreateView
from cyder.cydns.urls import cydns_urls


urlpatterns = cydns_urls('nameserver')


urlpatterns += patterns(
    '',
    url(r'(?P<domain>[\w-]+)/create_delegated/$',
        create_ns_delegated, name='nameserver-delegated-create'),
    url(r'(?P<domain>[\w-]+)/create/$',
        NSCreateView.as_view(), name='nameserver-by-domain-create'),
)
