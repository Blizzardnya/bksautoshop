from crispy_forms.helper import FormHelper
from django import forms


class CartAddProductForm(forms.Form):
    quantity = forms.DecimalField(label='Количество')
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

    def __init__(self, *args, is_weight_type: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_style = 'inline'

        if is_weight_type:
            self.fields['quantity'].widget.attrs.update(step='0.01', min='0.01', max='10000.0')
        else:
            self.fields['quantity'].widget.attrs.update(step='1', min='1', max='10000')
