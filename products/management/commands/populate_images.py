from django.core.management.base import BaseCommand


from products.models import Produto
from pybling.products import get_product


class Command(BaseCommand):
    help = '''Adiciona imagens de produtos quando configurado no bling'''

    def handle(self, *args, **options):
        produtos_local = Produto.objects.all()

        for produto in produtos_local:
            if produto.imagem is None:
                print('Produto', produto.codigo, 'sem imagem no banco local.')
                produto_bling = get_product(codigo=produto.codigo)
                produto_bling_imagem = produto_bling.json()['retorno']['produtos'][0]['produto']['imagem']
                if produto_bling_imagem:
                    print(produto_bling_imagem[0]['link'])
                    produto.imagem = produto_bling_imagem[0]['link']
                    produto.save()
                    print('Imagem salva para o produto', produto.codigo)
                else:
                    print('Produto', produto.codigo, 'sem imagem no bling.')
