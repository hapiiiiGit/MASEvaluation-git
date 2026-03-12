from django import forms
from .models import Donor
from django.utils import timezone

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'id',
            'name',
            'blood_type',
            'location',
            'contact_info',
            'last_donation',
            'is_active',
        ]
        widgets = {
            'id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control'}),
            'last_donation': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(DonorForm, self).__init__(*args, **kwargs)
        # If creating, generate a new id if not provided
        if not self.instance.pk:
            import uuid
            self.fields['id'].initial = str(uuid.uuid4())
            self.fields['id'].widget.attrs['readonly'] = True

    def clean_id(self):
        id = self.cleaned_data.get('id')
        if not id:
            import uuid
            id = str(uuid.uuid4())
        return id

    def clean_last_donation(self):
        last_donation = self.cleaned_data.get('last_donation')
        # Accept blank, otherwise ensure it's a valid datetime
        if last_donation is None or last_donation == '':
            return None
        return last_donation

    def save(self, commit=True):
        donor = super(DonorForm, self).save(commit=False)
        if commit:
            donor.save()
        return donor