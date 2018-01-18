from django import forms
from django.conf import settings
from django.utils.translation import pgettext_lazy
from payments import PaymentStatus

from ..registration.forms import SignupForm

class PasswordForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.HiddenInput()
