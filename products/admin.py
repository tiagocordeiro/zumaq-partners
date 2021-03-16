from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Produto, CustomCoeficiente, CustomCoeficienteItens, ProdutoAtacado, CustomBlocked, BlockedProducts


# Register your models here.
class ProdutoAtacadoInLine(admin.StackedInline):
    model = ProdutoAtacado
    extra = 1


class ProdutoAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ('codigo', 'descricao')
    actions = admin.ModelAdmin.actions + ['mass_change_selected']
    massadmin_exclude = ['codigo', 'descricao', 'pago_na_china', ]
    inlines = [
        ProdutoAtacadoInLine,
    ]


class CustomCoeficienteInline(admin.StackedInline):
    model = CustomCoeficienteItens
    extra = 1


class CustomCoeficienteAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ('parceiro',)
    inlines = [
        CustomCoeficienteInline,
    ]
    actions = admin.ModelAdmin.actions + ['mass_change_selected']
    massadmin_exclude = ['parceiro', ]


class BlockedProductInLine(admin.StackedInline):
    model = BlockedProducts
    extra = 1


class BlockedProductsAdmin(admin.ModelAdmin):
    list_display = ('parceiro',)
    inlines = [
        BlockedProductInLine,
    ]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(CustomCoeficiente, CustomCoeficienteAdmin)
admin.site.register(CustomBlocked, BlockedProductsAdmin)
