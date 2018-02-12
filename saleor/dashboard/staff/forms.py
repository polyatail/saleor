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
        password = forms.CharField(
          widget=forms.PasswordInput, required=False, max_length=30, label="Password")
        self.fields.update({"password": password})

    class Meta:
        model = User
        fields = ['username', 'company', 'password', 'is_staff', 'is_active']
