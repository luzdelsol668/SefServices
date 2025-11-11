from django import forms
from django.forms import TextInput, ChoiceField, Select, DateInput, EmailInput, ModelChoiceField, \
    ModelMultipleChoiceField, CheckboxSelectMultiple, RadioSelect, Textarea, CheckboxInput, FileInput
from django.forms.models import ModelChoiceIteratorValue
from django_countries.widgets import CountrySelectWidget

from rides.models import CarClass, Vehicle, PartnerCompany, Driver


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
                classes += "form-control b"
            else:
                classes = "form-control b"
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


class CategoryForm(ChangeInputsStyle):
    class Meta:
        model = CarClass
        fields = ['name', 'base_price', 'per_km_rate', 'per_hour_rate', 'min_hours', 'airport_fee', 'image']

        labels = {
            "name": "Nom de la Catégorie",
            "base_price": "Prix ordinaire",
            "per_km_rate": "Prix du Kilométrage",
            "per_hour_rate": "Prix Horaire",
            "min_hours": "Durée minimale",
            "airport_fee": "Frais d'Airport",
            "image": "Image de la Catégorie"
        }


class AddNewPartnerForm(ChangeInputsStyle):
    class Meta:
        model = PartnerCompany
        fields = ['name', 'phone', 'email', 'website', 'country']

        labels = {
            "name": "Nom du partenaire",
            "phone": "N° de Téléphone",
            "email": "Email de la compagnie",
            "website": "Website du partenaire",
            "country": "Pays"
        }


class AddVehicleForm(ChangeInputsStyle):
    class Meta:
        model = Vehicle
        fields = ['name']


class AddDriverForm(SingleStyle):
    lastname = forms.CharField(label="Nom du Chauffeur")
    firstname = forms.CharField(label="Prénom du Chauffeur")
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput())
    phone = forms.CharField(label="N° Tel")
    partner = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partner'].choices = [(c.id, c.name) for c in PartnerCompany.objects.all().order_by('-created_at')]









