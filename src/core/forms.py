from turtle import width

from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckOutForm(forms.Form):
    shipping_address1 = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)

    shipping_country = CountryField(blank_label='(select country)').formfield(required=False , widget=CountrySelectWidget(attrs={
        'class': 'form-dropdown'
    }))
    shipping_zip = forms.CharField(required=False)

    # BILLING ADDRESS
    billing_address1 = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)

    billing_country = CountryField(blank_label='(select country)').formfield(required=False , widget=CountrySelectWidget(attrs={
        'class': 'form-dropdown'
    }))

    billing_zip = forms.CharField(required=False)


    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class RefundForm(forms.Form):
    ref_code = forms.UUIDField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()