from django import forms


class AddContainerToOrderForm(forms.Form):
    container_number = forms.CharField(max_length=20, label="Номер контейнера")

    def __init__(self, *args, disabled_number: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['container_number'].disabled = disabled_number
        self.fields['container_number'].required = not disabled_number


class AddContainerToOrderItemForm(AddContainerToOrderForm):
    quantity = forms.DecimalField(label='Количество')

    def __init__(self, *args, disabled_number: bool = False, is_weight_type: bool = False, **kwargs):
        super().__init__(*args, disabled_number=disabled_number, **kwargs)

        if is_weight_type:
            self.fields['quantity'].widget.attrs.update(step='0.01', min='0.01', max='10000.0')
        else:
            self.fields['quantity'].widget.attrs.update(step='1', min='1', max='10000')
