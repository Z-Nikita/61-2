from django import forms


class RegisterForms(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
    password_confirm = forms.CharField(required=True)

    def clean(self):
        data = self.cleaned_data
        password = data.get("password")
        password_confirm = data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return data


class LoginForms(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
