from django.forms import ModelForm, NumberInput

from .models import Pedido, PedidoItem


class PedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = []


class PedidoItensForm(ModelForm):
    class Meta:
        model = PedidoItem
        fields = ['quantidade']
        widgets = {
            'quantidade': NumberInput(attrs={'class': 'form-control'}),
        }
