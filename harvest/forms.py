from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


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
