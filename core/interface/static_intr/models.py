from django.db import models
from django.core.exceptions import ValidationError

from systems.models import System

import mozdns
from core.keyvalue.models import KeyValue
from core.keyvalue.utils import AuxAttr
from core.mixins import ObjectUrlMixin
from core.validation import validate_mac
from mozdns.address_record.models import BaseAddressRecord
from mozdns.models import MozdnsRecord
from mozdns.view.models import View
from mozdns.domain.models import Domain
from mozdns.cname.models import CNAME
from mozdns.ip.models import Ip
from settings import CORE_BASE_URL

import re
import pdb


class StaticInterface(BaseAddressRecord, models.Model, ObjectUrlMixin):
    """The StaticInterface Class.

        >>> s = StaticInterface(label=label, domain=domain, ip_str=ip_str,
        ... ip_type=ip_type)
        >>> s.full_clean()
        >>> s.save()

    This class is the main interface to DNS and DHCP in mozinv. A static
    interface consists of three key pieces of information: Ip address, Mac
    Address, and Hostname (the hostname is comprised of a label and a domain).
    From these three peices of information, three things are ensured: An A or
    AAAA DNS record, a PTR record, and a `host` statement in the DHCP builds
    that grants the mac address of the interface the correct IP address and
    hostname.

    If you want an A/AAAA, PTR, and a DHCP lease, create on of these objects.

    In terms of DNS, a static interface represents a PTR and A record and must
    adhear to the requirements of those classes. The interface inherits from
    AddressRecord and will call it's clean method with 'update_reverse_domain'
    set to True. This will ensure that it's A record is valid *and* that it's
    PTR record is valid.

    """
    id = models.AutoField(primary_key=True)
    mac = models.CharField(max_length=17, validators=[validate_mac])
    reverse_domain = models.ForeignKey(Domain, null=True, blank=True,
            related_name='staticintrdomain_set')

    system = models.ForeignKey(System, null=True, blank=True)
    dhcp_enabled = models.BooleanField(default=True)
    dns_enabled = models.BooleanField(default=True)

    attrs = None

    def update_attrs(self):
        self.attrs = AuxAttr(StaticIntrKeyValue, self, 'intr')

    def details(self):
        return (
                ('Name', self.fqdn),
                ('DNS Type', 'A/PTR'),
                ('IP', self.ip_str),
                )

    class Meta:
        db_table = 'static_interface'
        unique_together = ('ip_upper', 'ip_lower', 'label', 'domain')

    def get_edit_url(self):
        return "/core/interface/{0}/update/".format(self.pk)

    def get_delete_url(self):
        return "/core/interface/{0}/delete/".format(self.pk)

    def get_absolute_url(self):
        return "/systems/show/{0}/".format(self.system.pk)

    def interface_name(self):
        self.update_attrs()
        try:
            itype, primary, alias = '', '', ''
            itype = self.attrs.interface_type
            primary = self.attrs.primary
            alias = self.attrs.alias
        except AttributeError:
            pass
        if not itype and not primary:
            return "None"
        if not alias:
            return "{0}{1}".format(itype, primary)
        return "{0}{1}.{2}".format(itype, primary, alias)

    def clean(self, *args, **kwargs):
        #if not isinstance(self.mac, basestring):
        #    raise ValidationError("Mac Address not of valid type.")
        #self.mac = self.mac.lower()
        if not self.system:
            raise ValidationError("An interface means nothing without it's "
                "system.")
        from mozdns.ptr.models import PTR
        if PTR.objects.filter(ip_str=self.ip_str, name=self.fqdn).exists():
            raise ValidationError("A PTR already uses this Name and IP")
        from mozdns.address_record.models import AddressRecord
        if AddressRecord.objects.filter(ip_str=self.ip_str, fqdn=self.fqdn
                ).exists():
            raise ValidationError("An A record already uses this Name and IP")

        if kwargs.pop('validate_glue', True):
            self.check_glue_status()

        super(StaticInterface, self).clean(validate_glue=False,
                update_reverse_domain=True, ignore_interface=True)

        if self.pk and self.ip_str.startswith('10.'):
            p = View.objects.filter(name='private')
            if p:
                self.views.add(p[0])
                super(StaticInterface, self).clean(validate_glue=False,
                        update_reverse_domain=True, ignore_interface=True)

    def check_glue_status(self):
        """If this interface is a 'glue' record for a Nameserver instance,
        do not allow modifications to this record. The Nameserver will
        need to point to a different record before this record can
        be updated.
        """
        if self.pk is None:
            return
        # First get this object from the database and compare it to the
        # Nameserver object about to be saved.
        db_self = StaticInterface.objects.get(pk=self.pk)
        if db_self.label == self.label and db_self.domain == self.domain:
            return
        # The label of the domain changed. Make sure it's not a glue record
        Nameserver = mozdns.nameserver.models.Nameserver
        if Nameserver.objects.filter(intr_glue=self).exists():
            raise ValidationError("This Interface represents aa glue record "
                    "for a Nameserver. Change the Nameserver to edit this "
                    "record.")

    def record_type(self):
        return "A/PTR"

    def delete(self, *args, **kwargs):
        if kwargs.pop('validate_glue', True):
            if self.intrnameserver_set.exists():
                raise ValidationError("Cannot delete the record {0}. It is a "
                    "glue record.".format(self.record_type()))
        check_cname = kwargs.pop("check_cname", True)
        super(StaticInterface, self).delete(validate_glue=False,
                check_cname=check_cname)

    def __repr__(self):
        return "<StaticInterface: {0}>".format(str(self))

    def __str__(self):
        #return "IP:{0} Full Name:{1} Mac:{2}".format(self.ip_str,
        #        self.fqdn, self.mac)
        return "IP:{0} Full Name:{1}".format(self.ip_str,
                self.fqdn)


is_eth = re.compile("^eth$")
is_mgmt = re.compile("^mgmt$")


class StaticIntrKeyValue(KeyValue):
    intr = models.ForeignKey(StaticInterface, null=False)

    class Meta:
        db_table = 'static_inter_key_value'
        unique_together = ('key', 'value', 'intr')

    def _aa_primary(self):
        """The primary number of this interface (I.E. eth1.0 would have a primary
        number of '1')"""
        if not self.value.isdigit():
            raise ValidationError("The primary number must be a number.")

    def _aa_alias(self):
        """The alias of this interface (I.E. eth1.0 would have a primary
        number of '0')."""
        if not self.value.isdigit():
            raise ValidationError("The alias number must be a number.")

    def _aa_interface_type(self):
        """Either eth (ethernet) of mgmt (mgmt)."""
        if not (is_eth.match(self.value) or is_mgmt.match(self.value)):
            raise ValidationError("Interface type must either be 'eth' "
                "or 'mgmt'")