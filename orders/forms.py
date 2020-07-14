from django import forms


class ContainerOrderAddForm(forms.Form):
    container_number = forms.CharField(max_length=20, label="Номер контейнера")

    def __init__(self, *args, disabled_number: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['container_number'].disabled = disabled_number
        self.fields['container_number'].required = not disabled_number


class ContainerWeightOrderItemAddForm(ContainerOrderAddForm):
    quantity = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label='Количество')


class ContainerPieceOrderItemAddForm(ContainerOrderAddForm):
    quantity = forms.IntegerField(min_value=1, label='Количество')
