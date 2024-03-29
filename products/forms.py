from django.forms import ModelForm, TextInput, Select, NumberInput, CheckboxInput

from .models import Produto, CustomCoeficiente, CustomCoeficienteItens, ProdutoAtacado, CustomBlocked, BlockedProducts


class ProdutoForm(ModelForm):
    class Meta:
        model = Produto
        fields = ['pago_na_china',
                  'reminmbi',
                  'dolar_cotado',
                  'impostos_na_china',
                  'porcentagem_importacao',
                  'coeficiente',
                  'imagem',
                  'active',
                  'dolar_automatico',
                  'fora_de_estoque', ]
        widgets = {
            'pago_na_china': TextInput(attrs={'class': 'form-control', 'placeholder': 'Pago na China'}),
            'reminmbi': TextInput(attrs={'class': 'form-control', 'placeholder': 'Reminmbi'}),
            'dolar_cotado': TextInput(attrs={'class': 'form-control', 'placeholder': 'Dolar Cotado'}),
            'impostos_na_china': TextInput(attrs={'class': 'form-control', 'placeholder': 'Impostos na China'}),
            'porcentagem_importacao': TextInput(attrs={'class': 'form-control', 'placeholder': '% Importação'}),
            'coeficiente': TextInput(attrs={'class': 'form-control', 'placeholder': 'Coeficiente'}),
            'imagem': TextInput(attrs={'class': 'form-control', 'placeholder': 'Url da imagem'}),
            'active': CheckboxInput(attrs={'class': 'form-control'}),
            'dolar_automatico': CheckboxInput(attrs={'class': 'form-control'}),
            'fora_de_estoque': CheckboxInput(attrs={'class': 'form-control'})
        }


class ProdutoAtacadoForm(ModelForm):
    class Meta:
        model = ProdutoAtacado
        fields = ['quantidade', 'coeficiente']
        widgets = {
            'quantidade': NumberInput(attrs={'class': 'form-control'}),
            'coeficiente': TextInput(attrs={'class': 'form-control', 'placeholder': 'Coeficiente'}),
        }


class CustomCoeficienteForm(ModelForm):
    class Meta:
        model = CustomCoeficiente
        fields = ['coeficiente_padrao']
        widgets = {
            'coeficiente_padrao': NumberInput(attrs={'class': 'form-control'}),
        }


class CustomCoeficienteItensForm(ModelForm):
    class Meta:
        model = CustomCoeficienteItens
        fields = ['parceiro', 'produto', 'coeficiente']
        widgets = {
            'parceiro': Select(attrs={'class': 'form-control', 'placeholder': 'Parceiro', 'disabled': ''}),
            'produto': Select(attrs={'class': 'form-control'}),
            'coeficiente': NumberInput(attrs={'class': 'form-control'}),
        }


class CustomBlockedForm(ModelForm):
    class Meta:
        model = CustomBlocked
        fields = ['parceiro']


class BlockedProductsForm(ModelForm):
    class Meta:
        model = BlockedProducts
        fields = ['parceiro', 'produto']
        widgets = {
            'parceiro': Select(attrs={'class': 'form-control', 'placeholder': 'Parceiro', 'disabled': ''}),
            'produto': Select(attrs={'class': 'form-control'}),
        }
