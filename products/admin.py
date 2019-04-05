from django.contrib import admin

from .models import Produto, CustomCoeficiente, CustomCoeficienteItens


# Register your models here.
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao')
    actions = admin.ModelAdmin.actions + ['mass_change_selected']
    massadmin_exclude = ['codigo', 'descricao', 'pago_na_china', ]

class CustomCoeficienteInline(admin.StackedInline):
    model = CustomCoeficienteItens
    extra = 1

class CustomCoeficienteAdmin(admin.ModelAdmin):
    list_display = ('parceiro',)
    inlines = [
        CustomCoeficienteInline,
    ]
    actions = admin.ModelAdmin.actions + ['mass_change_selected']
    massadmin_exclude = ['parceiro', ]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(CustomCoeficiente, CustomCoeficienteAdmin)
