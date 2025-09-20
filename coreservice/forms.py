from django import forms
from django.forms import TextInput, ChoiceField, Select, DateInput, EmailInput, ModelChoiceField, \
    ModelMultipleChoiceField, CheckboxSelectMultiple, RadioSelect, Textarea, CheckboxInput, FileInput
from django.forms.models import ModelChoiceIteratorValue
from django_countries.widgets import CountrySelectWidget

from accounts.models import Customer
from coreservice.models import *
from django.utils.translation import gettext_lazy as _


class ChangeInputsStyle(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add common css classes to all widgets
        for field in iter(self.fields):
            # get current classes from Meta
            classes = self.fields[field].widget.attrs.get("class")
            if classes is not None:
                classes += "form-control"
            else:
                classes = "form-control"
            self.fields[field].widget.attrs.update({
                'class': classes
            })


class SingleStyle(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add common css classes to all widgets
        for field in iter(self.fields):
            # get current classes from Meta
            classes = self.fields[field].widget.attrs.get("class")
            if classes is not None:
                classes += "form-control form-control-lg"
            else:
                classes = "form-control form-control-lg"
            self.fields[field].widget.attrs.update({
                'class': classes
            })


class MediumStyle(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add common css classes to all widgets
        for field in iter(self.fields):
            # get current classes from Meta
            classes = self.fields[field].widget.attrs.get("class")
            if classes is not None:
                classes += "form-control"
            else:
                classes = "form-control"
            self.fields[field].widget.attrs.update({
                'class': classes
            })


class LoginForm(forms.Form):
    email = forms.EmailField(label="", required=True, widget=forms.EmailInput(
        attrs={"placeholder": "example@example.com", 'class': 'form-control mt-3'}))
    password = forms.CharField(max_length=255, required=True, label="", widget=forms.PasswordInput(
        attrs={"placeholder": "******", 'class': 'form-control mt-3'}))


class RegistrationForm(ChangeInputsStyle):

    class Meta:
        model = Customer
        fields = ['last_name', 'first_name', 'email', 'phone', 'password']

        widgets = {
            "last_name": forms.TextInput(attrs={"placeholder": "Nom"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Prénom(s)"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "password": forms.PasswordInput(attrs={"placeholder": _("Password")}),
        }


class AdminNewPasswordForm(SingleStyle):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'readonly': True}))
    password = forms.CharField(max_length=255, label="Mot de passe",
                               widget=forms.PasswordInput(attrs={'autocomplete': "new-password"}))
    confirm_password = forms.CharField(max_length=255, label="Confirmer le mot de passe",
                                       widget=forms.PasswordInput(attrs={'autocomplete': "new-password"}))


class CustomerProfileForm(ChangeInputsStyle):

    class Meta:
        model = Customer
        fields = ['last_name', 'first_name', 'email', 'phone']

        labels = {
            "last_name": _("Last Name"),
            "first_name": _("First Name"),
            "email": _("Email"),
            "phone": _("Phone Number"),
        }

        widgets = {
            "last_name": forms.TextInput(attrs={"placeholder": "Nom"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Prénom(s)"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }


class EmailMarketingForm(ChangeInputsStyle):

    class Meta:
        model = Customer
        fields = ['is_marketing_enabled', 'is_email_enabled', 'is_sms_enabled']

        labels = {
            "is_marketing_enabled": _("Marketing emails"),
            "is_email_enabled": _("Email"),
            "is_sms_enabled": _("SMS")
        }

        widgets = {
            "is_marketing_enabled": forms.CheckboxInput(attrs={"class": "form-check-input d"}),
            "is_email_enabled": forms.CheckboxInput(attrs={"class": "form-check-input d"}),
            "is_sms_enabled": forms.CheckboxInput(attrs={"class": "form-check-input d"})
        }
























