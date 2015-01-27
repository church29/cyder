from django.conf.urls.defaults import patterns, url
from cyder.cydhcp.interface.views import is_last_interface
from cyder.cydhcp.interface.views import batch_update, batch_update_get_ranges

urlpatterns = patterns(
    '',
    url(r'^last_interface/', is_last_interface, name='is_last_interface'),
    url(r'^batch_update/', batch_update, name='batch_update'),
    url(r'^batch_update_get_ranges/', batch_update_get_ranges,
        name='batch_update_get_ranges'),
)
