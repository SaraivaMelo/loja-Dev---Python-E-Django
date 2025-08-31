import uuid
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile, Address

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Nome', max_length=30)
    last_name = forms.CharField(label='Sobrenome', max_length=150)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Gera username automático com UUID para evitar conflitos e exigência
        user.username = str(uuid.uuid4())[:30]

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields.pop('username', None)  # Remove o campo username do form
        self.fields['email'].widget.attrs.update({'class': 'form-control mt-2'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control mt-2'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control mt-2'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control mt-2'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control mt-2'})

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['cep', 'street', 'number', 'neighborhood', 'city', 'state']
        widgets = {
            field: forms.TextInput(attrs={'class': 'form-control mt-2', 'id': field})
            for field in fields
        }

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control mt-2', 'id': 'phone'})
        }
