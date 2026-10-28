from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Categoria, Empresa, Cliente, Produto, Pedido, ItemPedido


# Cadastro de Empresa (rota pública). Como Empresa herda de User, o
# UserCreationForm já traz username + senha (com confirmação e validadores);
# aqui só trocamos o model e acrescentamos os campos próprios da Empresa.
class EmpresaCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Empresa
        fields = ["username", "nome", "telefone", "endereco", "instrucoes_atendimento"]


# Form de Empresa: gera automaticamente os campos do model (menos o id),
# usado na edição (sem senha).
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