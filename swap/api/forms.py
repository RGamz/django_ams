from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Login")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)




