from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class BootstrapFormMixin:
    """Adds Bootstrap CSS classes to every field widget. Reused by all forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                css = "form-check-input"
            elif isinstance(widget, forms.Select):
                css = "form-select"
            else:
                css = "form-control"
            widget.attrs["class"] = (widget.attrs.get("class", "") + " " + css).strip()


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[(Profile.PLAYER, "Player (solve problems, join contests)"),
                 (Profile.HOST, "Host (create problems and contest rooms)")],
        initial=Profile.PLAYER,
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Profile was created by the signal; set the chosen role (never admin)
            user.profile.role = self.cleaned_data["role"]
            user.profile.save()
        return user


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio",)


class RoleForm(BootstrapFormMixin, forms.ModelForm):
    """Used by Admin to change a user's role."""

    class Meta:
        model = Profile
        fields = ("role",)
