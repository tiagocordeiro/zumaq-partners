from django.contrib import admin

from .models import Produto


# Register your models here.
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao')


admin.site.register(Produto, ProdutoAdmin)
