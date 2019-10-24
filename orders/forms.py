from django import forms
from crispy_forms.helper import FormHelper


class ContainerAddForm(forms.Form):
    container_number = forms.CharField(max_length=20, label="Номер контейнера")
