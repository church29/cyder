from django.db.models.loading import get_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse

from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.range_usage import range_usage
from cyder.cydhcp.network.utils import get_ranges
import json


def is_last_interface(request):
    obj_type = request.POST['obj_type']
    pk = request.POST['pk']
    Klass = get_model('cyder', obj_type.replace('_', ''))
    obj = get_object_or_404(Klass, pk=pk)
    last_interface = False
    if (len(DynamicInterface.objects.filter(system=obj.system))
            + len(StaticInterface.objects.filter(system=obj.system)) == 1):
        last_interface = True

    return HttpResponse(json.dumps({'last_interface': last_interface}))


def batch_update_get_ranges(request):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))
    ranges = []
    ctnr = request.session['ctnr']
    range_type = request.POST.get('range_type', None)
    if range_type:
        range_type = [range_type[:2]]
        range_qs = get_ranges([], ctnr, range_type, all_ranges=True)
    else:
        range_qs = get_ranges([], ctnr, all_ranges=True)

    for n, rng in enumerate(range_qs):
        ranges.append([rng.id, rng.__str__()])

    return HttpResponse(json.dumps({'ranges': ranges}))


def batch_update_same_type(rng, ip, intr, intr_type):
    if 'static' in intr_type:
        intr.ip_str = str(ip)
        intr.ip_type = rng.ip_type
    else:
        intr.range = rng

    return intr



def batch_update_different_type(rng, ip, intr, intr_type):
    new_intr_type = 'staticdynamicinterface'.replace(
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

    return NewInterface(**kwargs)


def batch_update(request):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))

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

    success = True
    ip = None
    start_lower = None
    intr_type = ('').join(request.POST['interface_type'].split()[:-1])
    new_intrs = []
    same_type = intr_type[:2] == rng.range_type
    Interface = get_model('cyder', intr_type + 'interface')
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
            new_intr = batch_update_same_type(rng, ip, intr, intr_type)

        else:
            new_intr = batch_update_different_type(rng, ip, intr, intr_type)

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
                break

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
