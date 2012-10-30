from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.cydns.cname.views import *

urlpatterns = patterns('',
   url(r'^$', CNAMEListView.as_view(), name='cname-list'),
   url(r'(?P<domain>[\w-]+)/create/$',
       csrf_exempt(CNAMECreateView.as_view()), name='cname-create'),
   url(r'create/$', csrf_exempt(CNAMECreateView.as_view()), name='cname-create'),
   url(r'(?P<pk>[\w-]+)/update/$',
       csrf_exempt(CNAMEUpdateView.as_view()), name='cname-update'),
   url(r'(?P<pk>[\w-]+)/delete/$',
       csrf_exempt(CNAMEDeleteView.as_view()), name='cname-delete'),
   url(r'(?P<pk>[\w-]+)/$',
       csrf_exempt(CNAMEDetailView.as_view()), name='cname-detail'),
)