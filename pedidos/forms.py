from django.forms import ModelForm, NumberInput, Textarea

from .models import Pedido, PedidoItem


class PedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['observacoes']
        widgets = {
            'observacoes': Textarea(attrs={'class': 'form-control'}),
        }


class PedidoItensForm(ModelForm):
    class Meta:
        model = PedidoItem
        fields = ['quantidade']
        widgets = {
            'quantidade': NumberInput(attrs={'class': 'form-control'}),
        }
