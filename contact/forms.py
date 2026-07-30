from django import forms

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="Leave this field empty",
    )

    class Meta:
        model = ContactMessage

        fields = [
            "name",
            "email",
            "subject",
            "message",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your name",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "you@example.com",
                    "autocomplete": "email",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "What is this about?",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your message here...",
                    "rows": 7,
                }
            ),
        }

    def clean_website(self):
        website = self.cleaned_data.get("website")

        if website:
            raise forms.ValidationError("Invalid submission.")

        return website
