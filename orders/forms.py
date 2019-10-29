from django import forms
from crispy_forms.helper import FormHelper


class ContainerOrderAddForm(forms.Form):
    container_number = forms.CharField(max_length=20, label="Номер контейнера")


class ContainerWeightOrderItemAddForm(forms.Form):
    container_number = forms.CharField(max_length=20, label="Номер")
    quantity = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label='Количество')


class ContainerWeightOrderItemAddFormDis(forms.Form):
    container_number = forms.CharField(max_length=20, label="Номер", disabled=True, required=False)
    quantity = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label='Количество')


class ContainerPieceOrderItemAddFormDis(forms.Form):
    container_number = forms.CharField(max_length=20, label="Номер", disabled=True, required=False)
    quantity = forms.IntegerField(min_value=1, label='Количество')
