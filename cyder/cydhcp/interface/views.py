from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.range_usage import range_usage
import json


def interface_delete(request):
    obj_type = request.POST['obj_type']
    pk = request.POST['pk']
    Klass = get_model('cyder', obj_type.replace('_', ''))
    obj = get_object_or_404(Klass, pk=pk)
    if (len(DynamicInterface.objects.filter(system=obj.system))
            + len(StaticInterface.objects.filter(system=obj.system)) == 1):
            return HttpResponse(json.dumps({'last': True}))
    else:
        return HttpResponse(json.dumps({'last': False}))


def batch_update(request):
    if request.POST:
        if not request.POST['range']:
            return HttpResponse(json.dumps({
                'error': 'That is not a valid choice'
                }))

        if not request.POST['interfaces']:
            return HttpResponse(json.dumps({
                'error': 'No interfaces selected'
                }))

        Range = get_model('range', 'range')
        rng = Range.objects.filter(id=request.POST['range'])
        if not rng.exists():
            return HttpResponse(json.dumps({
                'error': 'That is not a valid choice'
                }))

        rng = rng.get()
        if ',' in request.POST['interfaces']:
            interfaces = request.POST['interfaces'].split(',')
        else:
            interfaces = [request.POST['interfaces']]

        intr = request.POST['interface_type'].split(' ')[1].lower()
        Interface = get_model((intr + '_intr'), (intr + 'interface'))
        if intr == 'static':
            used_ips, _ = range_usage(
                rng.start_lower, rng.end_lower, rng.ip_type)
            if (len(interfaces) >
                    ((rng.end_lower - rng.start_lower) - len(used_ips))):
                return HttpResponse(json.dumps({
                    'error': 'Range does not have enough space for selected '
                    'interfaces'
                    }))
            else:
                interface_qs = Interface.objects.filter(pk__in=interfaces)
                for intr in interface_qs:
                    ip = rng.get_next_ip()
                    #update ip logic
                    intr.save()
        else:
            interface_qs = Interface.objects.filter(pk__in=interfaces)
            interface_qs.update(range=rng)
            for intr in interface_qs:
                intr.save()

        return HttpResponse(json.dumps({'success': True}))
