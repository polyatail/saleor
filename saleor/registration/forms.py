from django import forms
from django.contrib.auth import forms as django_forms
from django.utils.translation import pgettext

from saleor.userprofile.models import User


class LoginForm(django_forms.AuthenticationForm):
    username = forms.CharField(
        label=pgettext('Form field', 'Username'), max_length=64)

    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(request=request, *args, **kwargs)
        if request:
            username = request.GET.get('username')
            if username:
                self.fields['username'].initial = username


