from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.forms import BootstrapFormMixin
from problems.models import Problem

from .models import Room


class RoomForm(BootstrapFormMixin, forms.ModelForm):
    duration_minutes = forms.IntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(300)], initial=30,
        help_text="Contest length in minutes (5 to 300)",
    )
    problems = forms.ModelMultipleChoiceField(
        queryset=Problem.objects.none(), widget=forms.CheckboxSelectMultiple,
        help_text="Pick the problems for this contest",
    )

    class Meta:
        model = Room
        fields = ("title", "duration_minutes", "problems")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["problems"].queryset = Problem.objects.filter(is_published=True)

    def clean_problems(self):
        problems = self.cleaned_data["problems"]
        for problem in problems:
            if not problem.test_cases.exists():
                raise forms.ValidationError(f'"{problem.title}" has no test cases, so it cannot be judged.')
        return problems


class JoinForm(BootstrapFormMixin, forms.Form):
    code = forms.CharField(max_length=6, min_length=6, label="Room code",
                           widget=forms.TextInput(attrs={"placeholder": "e.g. A1B2C3", "style": "text-transform:uppercase"}))

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()
