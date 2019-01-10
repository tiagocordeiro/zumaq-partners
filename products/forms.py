from django.forms import ModelForm, TextInput

from .models import Produto


class ProdutoForm(ModelForm):
    class Meta:
        model = Produto
        fields = ['pago_na_china',
                  'reminmbi',
                  'dolar_cotado',
                  'impostos_na_china',
                  'porcentagem_importacao',
                  'coeficiente', ]
        widgets = {
            'pago_na_china': TextInput(attrs={'class': 'form-control', 'placeholder': 'Pago na China'}),
            'reminmbi': TextInput(attrs={'class': 'form-control', 'placeholder': 'Reminmbi'}),
            'dolar_cotado': TextInput(attrs={'class': 'form-control', 'placeholder': 'Dolar Cotado'}),
            'impostos_na_china': TextInput(attrs={'class': 'form-control', 'placeholder': 'Impostos na China'}),
            'porcentagem_importacao': TextInput(attrs={'class': 'form-control', 'placeholder': '% Importação'}),
            'coeficiente': TextInput(attrs={'class': 'form-control', 'placeholder': 'Coeficiente'}),
        }
