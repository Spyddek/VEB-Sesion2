from django import forms
from .models import Deal

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ["title", "price_original", "price_discount", "expires_at", "image_url", "merchant", "categories"]
