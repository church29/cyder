from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404, redirect
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


def get_ranges(request):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))

    Range = get_model('cyder', 'range')
    ctnr = request.session['ctnr']
    range_type = request.POST.get('range_type', None)
    ranges = []
    if range_type:
        ranges_qs = Range.objects.filter(ctnr=ctnr, range_type=range_type[:2])
        for rng in ranges_qs:
            ranges.append([rng.id, rng.__str__()])

        return HttpResponse(json.dumps({'ranges': ranges}))

    else:
        return HttpResponse(json.dumps({'error': True}))


def batch_update(request):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))

    if (not request.POST.get('range', None) or
            not request.POST.get('range_type', None)):
        return HttpResponse(json.dumps({
            'error': 'Please select a range and range type'}))

    if not request.POST.get('interfaces', None):
        return HttpResponse(json.dumps({
            'error': 'No interfaces selected'}))

    Range = get_model('cyder', 'range')
    rng = Range.objects.filter(id=request.POST['range'])
    if not rng.exists():
        return HttpResponse(json.dumps({
            'error': 'That range does not exist'}))

    rng = rng.get()
    print rng.range_type
    interfaces = request.POST['interfaces'].split(',')
    intr_type = request.POST['interface_type'].split(' ')[1].lower()
    Interface = get_model('cyder', (intr_type + 'interface'))
    if Interface.__name__ == 'StaticInterface':
        if rng.range_type == 'st':
            used_ips, _ = range_usage(
                rng.start_lower, rng.end_lower, rng.ip_type)
            if (len(interfaces) >
                    ((rng.end_lower - rng.start_lower) - len(used_ips))):
                return HttpResponse(json.dumps({
                    'error': 'Range does not have enough space for selected '
                    'interfaces'}))
            else:
                interface_qs = Interface.objects.filter(pk__in=interfaces)
                for intr in interface_qs:
                    ip = rng.get_next_ip()

                    #update ip logic
                    intr.save()
        else:
            interface_qs = Interface.objects.filter(pk__in=interfaces)
            dynamic_intrs = []
            for intr in interface_qs:
                #migrate to dynamic
                intr.save()

    else:
        interface_qs = Interface.objects.filter(pk__in=interfaces)
        interface_qs.update(range=rng)
        for intr in interface_qs:
            intr.save()

    return HttpResponse(json.dumps({'success': True}))
