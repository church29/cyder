from django import forms

from cyder.cydhcp.range.models import Range
from cyder.base.mixins import UsabilityFormMixin


class BatchInterfaceForm(forms.Form, UsabilityFormMixin):
    range_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('static', 'Static'),
            ('dynamic', 'Dynamic')))
    range = forms.ModelChoiceField(queryset=Range.objects.all())
