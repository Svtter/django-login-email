from django import forms


class LoginForm(forms.Form):
    """Just check the login request."""

    email = forms.EmailField(label="email")
