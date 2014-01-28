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
    # going to be used when one interface fails
    # we reset all interfaces back to there original state
    success = True
    site = None
    ip = None
    start_lower = None
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
    rng_qs = Range.objects.filter(id=request.POST['range'])
    if not rng_qs.exists():
        return HttpResponse(json.dumps({
            'error': 'That range does not exist'}))

    rng = rng_qs.get()
    site_id = request.POST.get('site', None)
    if site_id:
        Site = get_model('cyder', 'site')
        site_qs = Site.objects.filter(id=site_id)
        if not site_qs.exists():
            return HttpResponse(json.dumps({
                'error': 'That site does not exist'}))

        site = site_qs.get()

    interfaces = request.POST['interfaces'].split(',')
    intr_type = request.POST['interface_type'].split(' ')[1].lower()
    Interface = get_model('cyder', (intr_type + 'interface'))
    interface_qs = Interface.objects.filter(pk__in=interfaces)
    intrs = []
    new_intrs = []
    if Interface.__name__ == 'StaticInterface':
        if rng.range_type == 'st':
            used_ips, _ = range_usage(
                rng.start_lower, rng.end_lower, rng.ip_type)
            if (len(interfaces) >
                    (((rng.end_lower - rng.start_lower) + 1) - len(used_ips))):
                return HttpResponse(json.dumps({
                    'error': 'Range does not have enough space for selected '
                    'interfaces'}))

            for intr in interface_qs:
                if ip:
                    start_lower = ip._ip + 1

                ip = rng.get_next_ip(start_lower=start_lower)
                intr.ip_str = str(ip)
                intr.ip_type = rng.ip_type
                if site:
                    intr.site = site
                try:
                    intr.full_clean()
                    intrs.append(intr)
                except:
                    return HttpResponse(json.dumps({
                        'error': 'Batch update was unsuccessful'}))
            for intr in intrs:
                intr.save()

        else:
            DynamicInterface = get_model('cyder', 'dynamicinterface')
            for intr in interface_qs:
                intrs.append(intr)
                new_intr = DynamicInterface(
                    mac=intr.mac, range=rng, dhcp_enabled=intr.dhcp_enabled,
                    ctnr=intr.ctnr, workgroup=intr.workgroup,
                    system=intr.system)
                new_intrs.append(new_intr)
                try:
                    intr.full_clean()
                except:
                    return HttpResponse(json.dumps({
                        'error': 'Batch update was unsuccessful'}))

            for intr in new_intrs:
                try:
                    intr.save()
                except:
                    success = False

            if success is True:
                interface_qs.delete()
            else:
                for intr in new_intrs:
                    intr.delete()

                return HttpResponse(json.dumps({
                    'error': 'Batch update was unsuccessful'}))

    else:
        if rng.range_type == 'dy':
            interface_qs.update(range=rng)
            if site:
                interface_qs.update(site=site)
            for intr in interface_qs:
                try:
                    intr.full_clean()
                    intrs.append(intr)
                except:
                    return HttpResponse(json.dumps({
                        'error': 'Batch update was unsuccessful'}))

            for intr in intrs:
                intr.save()
        else:
            used_ips, _ = range_usage(
                rng.start_lower, rng.end_lower, rng.ip_type)
            if (len(interfaces) >
                    (((rng.end_lower - rng.start_lower) + 1) - len(used_ips))):
                return HttpResponse(json.dumps({
                    'error': 'Range does not have enough space for selected '
                    'interfaces'}))

            StaticInterface = get_model('cyder', 'staticinterface')
            for intr in interface_qs:
                intrs.append(intr)
                if ip:
                    start_lower = ip._ip + 1

                ip = rng.get_next_ip(start_lower=start_lower)
                label = "{0}-{1}".format(intr.system.name, intr.mac)
                new_intr = StaticInterface(
                    mac=intr.mac, ip_str=str(ip), label=label,
                    ctnr=intr.ctnr, workgroup=intr.workgroup,
                    domain=rng.domain, system=intr.system,
                    ip_type=rng.ip_type, dhcp_enabled=intr.dhcp_enabled)
                new_intrs.append(new_intr)
                try:
                    intr.full_clean()
                except:
                    return HttpResponse(json.dumps({
                        'error': 'Batch update was unsuccessful'}))

            for intr in new_intrs:
                try:
                    intr.save()
                except:
                    success = False

            if success is True:
                interface_qs.delete()
            else:
                for intr in new_intrs:
                    intr.delete()

                return HttpResponse(json.dumps({
                    'error': 'Batch update was unsuccessful'}))

    return HttpResponse(json.dumps({'success': True}))
