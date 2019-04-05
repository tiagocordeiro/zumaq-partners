from django.contrib import admin

from .models import Pedido, PedidoItem


class PedidoInline(admin.StackedInline):
    model = PedidoItem
    extra = 1


class PedidoAdmin(admin.ModelAdmin):
    list_display = ('parceiro', 'status')
    inlines = [
        PedidoInline,
    ]
    actions = admin.ModelAdmin.actions + ['mass_change_selected']
    massadmin_exclude = ['parceiro', ]


admin.site.register(Pedido, PedidoAdmin)
