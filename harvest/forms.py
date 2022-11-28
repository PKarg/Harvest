from datetime import date
from typing import Optional

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from .models import Harvest


class HarvestForm(forms.ModelForm):

    class Meta:
        model = Harvest
        fields = ("date", "fruit", "amount", "price")

        widgets = {
            "date": forms.widgets.DateInput(format=("%Y-%m-%d"), attrs={"type": "date"}),
            "owner": forms.HiddenInput()
        }

        error_messages = {
            "date": {
                "invalid": "Earliest accepted harvest year is 1997"
            },

            "price": {
                "max_digits": "Price can have no more than 4 digits, including 2 decimal places",
                "max_decimal_places": "Price can have max 2 decimal places",
                "min_value": "Price can have minimal value of 0.1",
                "max_value": "Price can't have value over 50.0"
            },

            "amount": {
                "min_value": "Amount harvested can't be lower than 10",
                "max_value": "Amount harvested can't be higher than 5000"
            },


            NON_FIELD_ERRORS: {
                'unique': "Harvest with specified date and fruit already exists"
            }

        }

    def __init__(self, owner: User, h_id: Optional[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.h_id = h_id
        self.fields['date'].widget.attrs.update({"class": "harvest-date"})
        self.fields['fruit'].widget.attrs.update({"class": "harvest-fruit"})
        self.fields['amount'].widget.attrs.update({"class": "harvest-amount"})
        self.fields['price'].widget.attrs.update({"class": "harvest-price"})

    def clean(self):
        cleaned_data = super().clean()

        for f in self.fields:
            if not cleaned_data.get(f):
                raise forms.ValidationError(f"Field {f} can't be empty")

        h_date = cleaned_data.get("date")
        h_fruit = cleaned_data.get("fruit")

        h_owner = self.owner
        h_id = self.h_id

        if h_date:
            if h_date < date(year=1997, month=1, day=1):
                raise forms.ValidationError("Earliest accepted harvest year is 1997")

        if Harvest.objects.filter(date=h_date).filter(owner=h_owner)\
                .filter(fruit=h_fruit).exclude(id=h_id).first():
            raise forms.ValidationError("Harvest with given fruit and date already exists")


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
