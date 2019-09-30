from django import forms
from crispy_forms.helper import FormHelper


class CartAddProductForm(forms.Form):
    quantity = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label='Количество')
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
    helper = FormHelper()
    helper.form_show_labels = False

    quantity.widget.attrs.update(step=0.01)