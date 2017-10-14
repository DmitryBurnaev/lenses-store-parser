from django import forms
from django.forms import HiddenInput

from main.models import Product, ProfileCustomization


class FilterForm(forms.ModelForm):
    has_action = forms.NullBooleanField(required=False)

    class Meta:
        model = Product
        fields = ('has_action', 'brand', 'name')

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['has_action'].widget.attrs['class'] = 'form-control'
        self.fields['brand'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].required = False

    def clean(self):
        clean_data = super(FilterForm, self).clean()
        null_keys = [key for key, v in clean_data.items() if v is None]
        for k in null_keys:
            del clean_data[k]
        if clean_data['name']:
            clean_data['name__icontains'] = clean_data['name']
        del clean_data['name']
        return clean_data


class ProfileCustomizationForm(forms.ModelForm):
    """ Форма для кастомизации профиля пользователя """

    class Meta:
        model = ProfileCustomization
        fields = ('template', 'user')
        widgets = {'user': HiddenInput()}
