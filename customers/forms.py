from django import forms
from account.models import User, UserProfile

class UserProfileForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Start typing...", "required": "required"}
        )
    )
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}), required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            "profile_picture",
            "address",
            "country",
            "state",
            "city"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})