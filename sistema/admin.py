from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Cadastro, Categoria, Cliente, Empresa, ItemPedido, Pedido, Produto

@admin.register(Empresa)
class EmpresaAdmin(UserAdmin):
    list_display = ["username", "nome", "telefone"]
    search_fields = ["username", "nome", "telefone"]
    fieldsets = UserAdmin.fieldsets + (
        ("Dados da empresa", {"fields": ["nome", "telefone", "endereco", "instrucoes_atendimento"]}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Dados da empresa", {"fields": ["nome", "telefone", "endereco", "instrucoes_atendimento"]}),
    )



@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "empresa", "ativo"]
    list_filter = ["empresa", "ativo"]
    search_fields = ["nome"]


class CadastroInline(admin.TabularInline):
    model = Cadastro
    extra = 1


@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    list_display = ["empresa", "cliente", "dataCadastro"]
    list_filter = ["empresa"]


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone"]
    list_filter = ["empresa"]
    search_fields = ["nome", "telefone"]
    inlines = [CadastroInline]



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