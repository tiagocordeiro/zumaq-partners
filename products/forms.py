from django.forms import ModelForm

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
