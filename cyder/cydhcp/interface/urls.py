from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.interface.views import interface_delete
from cyder.cydhcp.interface.views import batch_update

urlpatterns = patterns(
    '',
    url(r'^interface_delete/', interface_delete, name='interface-delete'),
    url(r'^batch_update/', batch_update, name='batch-update'),
)
