from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.forms import BootstrapFormMixin

from .models import Problem, TestCase


class ProblemForm(BootstrapFormMixin, forms.ModelForm):
    points = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)], initial=100)
    time_limit = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], initial=2,
        help_text="Seconds allowed per test case (1 to 10)",
    )

    class Meta:
        model = Problem
        fields = ("title", "description", "difficulty", "points", "time_limit", "is_published")
        widgets = {"description": forms.Textarea(attrs={"rows": 8})}

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        return title


class TestCaseForm(BootstrapFormMixin, forms.ModelForm):
    __test__ = False

    class Meta:
        model = TestCase
        fields = ("input_data", "expected_output", "is_sample")
        widgets = {
            "input_data": forms.Textarea(attrs={"rows": 3}),
            "expected_output": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_expected_output(self):
        value = self.cleaned_data["expected_output"]
        if not value.strip():
            raise forms.ValidationError("Expected output cannot be empty.")
        return value
