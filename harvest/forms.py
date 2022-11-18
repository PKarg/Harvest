from datetime import date

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

from .models import Harvest


class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ("date", "fruit", "amount", "price")
        widgets = {
            "date": forms.widgets.DateInput(format=("%Y-%m-%d"), attrs={"type": "date"})
        }
        error_messages = {
            "date": {
                "invalid": "Harvest date has to be at least in year 1997"
            }
        }

    def clean(self):
        cleaned_data = super().clean()
        h_date = cleaned_data["date"]
        if h_date:
            if h_date < date(year=1997, month=1, day=1):
                raise forms.ValidationError("Earliest accepted harvest year is 1997")

    def __init__(self, *args, **kwargs):
        super(HarvestForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({"class": "harvest-date"})
        self.fields['fruit'].widget.attrs.update({"class": "harvest-fruit"})
        self.fields['amount'].widget.attrs.update({"class": "harvest-amount"})
        self.fields['price'].widget.attrs.update({"class": "harvest-price"})


class CustomSignupForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'auth'})
        self.fields['password1'].widget.attrs.update({'class': 'auth'})
        self.fields['password2'].widget.attrs.update({'class': 'auth'})


class CustomLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'auth'})
        self.fields['password'].widget.attrs.update({'class': 'auth'})
