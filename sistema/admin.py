from django.contrib import admin

from .models import Categoria, Cliente, Empresa, ItemPedido, Pedido, Produto


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone",]
    search_fields = ["nome", "telefone"]


admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "empresa", "ativo"]
    list_filter = ["empresa", "ativo"]
    search_fields = ["nome"]


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone", "empresa"]
    list_filter = ["empresa"]
    search_fields = ["nome", "telefone"]


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ["nome", "categoria", "preco", "ativo"]
    list_filter = ["categoria", "ativo"]
    search_fields = ["nome"]



class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "status", "criado_em"]
    list_filter = ["status"]
    search_fields = ["cliente__nome"]
    inlines = [ItemPedidoInline]


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ["pedido", "produto", "quantidade"]
    list_filter = ["produto"]