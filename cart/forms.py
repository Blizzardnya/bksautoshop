from crispy_forms.helper import FormHelper
from django import forms


class AbstractCartAddProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_style = 'inline'

    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartAddWeightProductForm(AbstractCartAddProductForm):
    quantity = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label='Количество')


class CartAddPieceProductForm(AbstractCartAddProductForm):
    quantity = forms.IntegerField(min_value=1, label='Количество')
