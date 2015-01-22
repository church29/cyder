from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.interface.views import is_last_interface
from cyder.cydhcp.interface.views import batch_update, get_ranges

urlpatterns = patterns(
    '',
    url(r'^last_interface/', is_last_interface, name='is_last_interface'),
    url(r'^batch_update/', batch_update, name='batch-update'),
    url(r'^get_ranges/', get_ranges, name='get_ranges'),
)
