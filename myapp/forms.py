from django import forms

class LoginForm(forms.Form):
    login_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'text-input', 'style': 'background-image: url("/static/myapp/id_input.png");'})
    )
    login_pw = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'text-input', 'style': 'background-image: url("/static/myapp/pw_input.png");'})
    )