from django import forms
from .models import Deal

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = [
            "title",
            "price_original",
            "price_discount",
            "expires_at",
            "image_url",
            "merchant",
            "categories",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Введите описание акции...",
                "style": "resize: vertical;",
            }),
        }