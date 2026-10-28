from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Categoria, Empresa, Cliente, Produto, Pedido, ItemPedido

# Pedidos nesses status não aceitam mais itens (criar, editar ou excluir).
PEDIDO_STATUS_FECHADOS = ("cancelado", "finalizado")


# Cadastro de Empresa (rota pública). Como Empresa herda de User, o
# UserCreationForm já traz username + senha (com confirmação e validadores);
# aqui só trocamos o model e acrescentamos os campos próprios da Empresa.
class EmpresaCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Empresa
        fields = ["username", "nome", "telefone", "endereco", "instrucoes_atendimento"]


# Edição da Empresa (sem senha): nome, telefone, endereço e instruções.
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nome", "telefone", "endereco", "instrucoes_atendimento"]


# Categoria: a empresa NÃO é um campo do form; a view grava a empresa logada.
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "descricao", "ativo"]


# Cliente: sem campo empresa; a view cria o Cadastro ligando à empresa logada.
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "endereco", "observacoes"]


# Produto: a seleção de categoria mostra só as categorias da empresa logada.
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["categoria", "nome", "descricao", "preco", "imagem", "ativo"]

    def __init__(self, *args, empresa, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = Categoria.objects.filter(empresa=empresa)


# Pedido: a seleção de cliente mostra só os clientes da empresa logada.
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["cliente", "status"]

    def __init__(self, *args, empresa, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(empresa=empresa)


# ItemPedido: pedidos e produtos limitados à empresa logada, e não aceita
# pedido cancelado ou finalizado.
class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ["pedido", "produto", "quantidade"]

    def __init__(self, *args, empresa, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pedido"].queryset = Pedido.objects.filter(cliente__empresa=empresa)
        self.fields["produto"].queryset = Produto.objects.filter(categoria__empresa=empresa)

    def clean_pedido(self):
        pedido = self.cleaned_data["pedido"]
        if pedido.status in PEDIDO_STATUS_FECHADOS:
            raise forms.ValidationError(
                f"Não é possível adicionar itens a um pedido {pedido.get_status_display().lower()}."
            )
        return pedido