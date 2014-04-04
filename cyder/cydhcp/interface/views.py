from django.db.models.loading import get_model
from django.core.exceptions import ValidationError
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
        if ctnr.name == 'global':
            ranges_qs = Range.objects.filter(range_type=range_type[:2])
        else:
            ranges_qs = Range.objects.filter(
                ctnr=ctnr, range_type=range_type[:2])

        for rng in ranges_qs:
            ranges.append([rng.id, rng.__str__()])
        return HttpResponse(json.dumps({'ranges': ranges}))

    else:
        return HttpResponse(json.dumps({'error': True}))


def batch_update(request):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))

    success = True
    ip = None
    start_lower = None
    intr_type = request.POST['interface_type']
    new_intrs = []

    for field in ['range', 'range_type', 'interfaces']:
        if not request.POST.get(field, None):
            field = ' '.join(field.split('_'))
            return HttpResponse(json.dumps({
                'error': 'Please select {0}'.format(field)}))

    Range = get_model('cyder', 'range')
    rng_qs = Range.objects.filter(id=request.POST['range'])
    if rng_qs.exists():
        rng = rng_qs.get()
    else:
        return HttpResponse(json.dumps({
            'error': 'That range does not exist'}))

    same_type = intr_type[:2] == rng.range_type
    Interface = get_model('cyder', ('').join(intr_type.split())[:-1])
    interfaces = request.POST['interfaces'].split(',')
    interface_qs = Interface.objects.filter(pk__in=interfaces)
    if rng.range_type == 'st':
        used_ips, _ = range_usage(
            rng.start_lower, rng.end_lower, rng.ip_type)
        if (len(interfaces) >
                (((rng.end_lower - rng.start_lower) + 1) - len(used_ips))):
            return HttpResponse(json.dumps({
                'error': 'Range does not have enough space for selected '
                'interfaces'}))

    for intr in interface_qs:
        if rng.range_type == 'st':
            if ip:
                start_lower = ip._ip + 1

            ip = rng.get_next_ip(start_lower=start_lower)

        if same_type:
            if 'static' in intr_type:
                intr.ip_str = str(ip)
                intr.ip_type = rng.ip_type
            else:
                intr.range = rng

            new_intr = intr

        else:
            new_intr_type = 'staticinterfacedynamicinterface'.replace(
                intr_type, '')
            NewInterface = get_model('cyder', new_intr_type)
            kwargs = {'mac': intr.mac, 'dhcp_enabled': intr.dhcp_enabled,
                      'ctnr': intr.ctnr, 'workgroup': intr.workgroup,
                      'system': intr.system}
            if 'static' in new_intr_type:
                label = '{0}-{1}'.format(intr.system.name, intr.mac)
                kwargs.update({'ip_str': str(ip), 'ip_type': rng.ip_type,
                               'dns_enabled': True, 'domain': rng.domain,
                               'label': label})
            else:
                kwargs.update({'range': rng})

            new_intr = NewInterface(**kwargs)

        try:
            intr.full_clean()
            new_intrs.append(new_intr)
        except ValidationError as e:
            return HttpResponse(json.dumps({
                'error': 'Batch update was unsuccessful: {0}'.format(str(e))}))
    if same_type:
        for intr in new_intrs:
            intr.save()
    else:
        for intr in new_intrs:
            try:
                intr.save()
            except ValidationError as e:
                success = False

        if success:
            interface_qs.delete()
            rng.save()
        else:
            for intr in new_intrs:
                intr.delete()

            rng.save()
            return HttpResponse(json.dumps({
                'error': 'Batch update was unsuccessful: {0}'.format(str(e))}))

    return HttpResponse(json.dumps({'success': True}))
