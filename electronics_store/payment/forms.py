from django import forms


class PaymentForm(forms.Form):
    confirm = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.HiddenInput
    )
