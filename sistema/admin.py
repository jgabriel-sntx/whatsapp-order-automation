from django.contrib import admin

from .models import Categoria, Cliente, Empresa, ItemPedido, Pedido, Produto


# =============================================================================
# EMPRESA
# =============================================================================
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone", "user"]
    search_fields = ["nome", "telefone"]


# =============================================================================
# CATEGORIA
# =============================================================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "empresa", "ativo"]
    list_filter = ["empresa", "ativo"]
    search_fields = ["nome"]
