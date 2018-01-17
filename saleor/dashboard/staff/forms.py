from django import forms

from ...userprofile.models import User


class StaffForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        #kwargs.update(initial={'is_staff': True})
        super(StaffForm, self).__init__(*args, **kwargs)
        if self.user == self.instance:
            self.fields['is_staff'].disabled = True
            self.fields['is_active'].disabled = True
        #import pdb; pdb.set_trace()
        password = forms.CharField(
          widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=True)), label="Password")
        self.fields.update({"password": password})

    class Meta:
        model = User
        fields = ['email', 'company', 'password', 'is_staff', 'is_active']
