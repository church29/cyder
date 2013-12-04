from django.conf.urls.defaults import patterns, url

from cyder.cydhcp.interface.views import (
    batch_update, get_ranges, interface_delete)

urlpatterns = patterns(
    '',
    url(r'^interface_delete/', interface_delete, name='interface-delete'),
    url(r'^batch_update/', batch_update, name='batch-update'),
    url(r'^get_ranges/', get_ranges, name='get_ranges'),
)
