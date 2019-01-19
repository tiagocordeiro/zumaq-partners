from django.contrib import admin

from .models import Produto, CustomCoeficiente, CustomCoeficienteItens


# Register your models here.
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao')

class CustomCoeficienteInline(admin.StackedInline):
    model = CustomCoeficienteItens
    extra = 1

class CustomCoeficienteAdmin(admin.ModelAdmin):
    list_display = ('parceiro',)
    inlines = [
        CustomCoeficienteInline,
    ]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(CustomCoeficiente, CustomCoeficienteAdmin)
