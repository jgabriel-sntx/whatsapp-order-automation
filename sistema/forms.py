from django import forms

from .models import Categoria, Empresa, Cliente, Produto, Pedido, ItemPedido


# Form de Empresa: gera automaticamente os campos do model (menos o id),
# usado tanto na criação quanto na edição.
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nome", "telefone", "endereco", "instrucoes_atendimento"]


# Form de Categoria: empresa dona da categoria, nome, descrição e se está ativa.
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["empresa", "nome", "descricao", "ativo"]


# Form de Cliente: empresa dona do cadastro, nome, telefone, endereço e observações.
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["empresa", "nome", "telefone", "endereco", "observacoes"]


# Form de Produto: categoria, nome, descrição, preço, imagem e se está ativo.
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["categoria", "nome", "descricao", "preco", "imagem", "ativo"]


# Form de Pedido: só cliente e status — "criado_em" é preenchido
# automaticamente pelo model (auto_now_add) e não entra no form.
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["cliente", "status"]


# Form de ItemPedido: a qual pedido pertence, qual produto e a quantidade.
class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ["pedido", "produto", "quantidade"]