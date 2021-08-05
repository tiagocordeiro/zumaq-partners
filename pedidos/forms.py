from django.forms import ModelForm, NumberInput, Textarea, CheckboxInput

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


class PedidoSeparacaoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['separado']
        widgets = {
            'separado': CheckboxInput(attrs={'class': 'form-control'})
        }


class PedidoItensSeparacaoForm(ModelForm):
    class Meta:
        model = PedidoItem
        fields = ['separado', 'separado_nota', 'separado_imagem']
        widgets = {
            'separado': CheckboxInput(attrs={'class': 'form-control'}),
            'separado_nota': Textarea(attrs={'class': 'form-control'})
        }
