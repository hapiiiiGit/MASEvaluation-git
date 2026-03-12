from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import AdminUser

class AdminUserForm(UserCreationForm):
    """
    Form for creating and editing admin users.
    Includes password handling and role selection.
    """
    role = forms.ChoiceField(
        choices=AdminUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Role"
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Active"
    )

    class Meta:
        model = AdminUser
        fields = [
            'username',
            'email',
            'role',
            'is_active',
            'password1',
            'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super(AdminUserForm, self).save(commit=False)
        user.role = self.cleaned_data['role']
        user.is_active = self.cleaned_data['is_active']
        if commit:
            user.save()
        return user

class AdminUserChangeForm(UserChangeForm):
    """
    Form for updating admin users.
    """
    role = forms.ChoiceField(
        choices=AdminUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Role"
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Active"
    )

    class Meta:
        model = AdminUser
        fields = [
            'username',
            'email',
            'role',
            'is_active',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }