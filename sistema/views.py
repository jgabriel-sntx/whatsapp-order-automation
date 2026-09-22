from django import forms
from django.shortcuts import get_object_or_404, redirect, render

from .models import Categoria, Empresa, Cliente, Produto, Pedido, ItemPedido


# Página inicial com o menu de navegação (definido em base.html).
def index(request):
    return render(request, "index.html")


# =============================================================================
# EMPRESA
# =============================================================================

# Form de Empresa: gera automaticamente os campos do model (menos o id),
# usado tanto na criação quanto na edição.
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["user", "nome", "telefone", "endereco", "instrucoes_atendimento"]


# Lista todas as empresas cadastradas.
def empresa_list(request):
    empresas = Empresa.objects.all()
    return render(request, "empresa/list.html", {"empresas": empresas})


# Mostra os detalhes de uma empresa específica (404 se o pk não existir).
def empresa_detail(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    return render(request, "empresa/detail.html", {"empresa": empresa})


# Exibe o formulário (GET) e cria uma nova empresa (POST); redireciona
# para a tela de detalhe da empresa recém-criada.
def empresa_create(request):
    if request.method == "POST":
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save()
            return redirect("empresa_detail", pk=empresa.pk)
    else:
        form = EmpresaForm()
    return render(request, "empresa/form.html", {"form": form})


# Exibe o formulário pré-preenchido (GET) e salva as alterações (POST)
# de uma empresa já existente.
def empresa_update(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == "POST":
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect("empresa_detail", pk=empresa.pk)
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, "empresa/form.html", {"form": form})


# Pede confirmação (GET) e exclui a empresa (POST), voltando para a lista.
def empresa_delete(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == "POST":
        empresa.delete()
        return redirect("empresa_list")
    return render(request, "empresa/confirm_delete.html", {"empresa": empresa})


# =============================================================================
# CATEGORIA
# =============================================================================

# Form de Categoria: empresa dona da categoria, nome, descrição e se está ativa.
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["empresa", "nome", "descricao", "ativo"]


# Lista todas as categorias cadastradas.
def categoria_list(request):
    categorias = Categoria.objects.all()
    return render(request, "categoria/list.html", {"categorias": categorias})


# Mostra os detalhes de uma categoria específica.
def categoria_detail(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    return render(request, "categoria/detail.html", {"categoria": categoria})


# Exibe o formulário (GET) e cria uma nova categoria (POST).
def categoria_create(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            return redirect("categoria_detail", pk=categoria.pk)
    else:
        form = CategoriaForm()
    return render(request, "categoria/form.html", {"form": form})


# Exibe o formulário pré-preenchido (GET) e salva as alterações (POST).
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect("categoria_detail", pk=categoria.pk)
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, "categoria/form.html", {"form": form})


# Pede confirmação (GET) e exclui a categoria (POST).
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        categoria.delete()
        return redirect("categoria_list")
    return render(request, "categoria/confirm_delete.html", {"categoria": categoria})


# =============================================================================
# CLIENTE
# =============================================================================

# Form de Cliente: empresa dona do cadastro, nome, telefone, endereço e observações.
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["empresa", "nome", "telefone", "endereco", "observacoes"]


# Lista todos os clientes cadastrados.
def cliente_list(request):
    clientes = Cliente.objects.all()
    return render(request, "cliente/list.html", {"clientes": clientes})


# Mostra os detalhes de um cliente específico.
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, "cliente/detail.html", {"cliente": cliente})


# Exibe o formulário (GET) e cria um novo cliente (POST).
def cliente_create(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return redirect("cliente_detail", pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, "cliente/form.html", {"form": form})


# Exibe o formulário pré-preenchido (GET) e salva as alterações (POST).
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect("cliente_detail", pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "cliente/form.html", {"form": form})


# Pede confirmação (GET) e exclui o cliente (POST).
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        cliente.delete()
        return redirect("cliente_list")
    return render(request, "cliente/confirm_delete.html", {"cliente": cliente})


# =============================================================================
# PRODUTO
# =============================================================================

# Form de Produto: categoria, nome, descrição, preço, imagem e se está ativo.
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["categoria", "nome", "descricao", "preco", "imagem", "ativo"]


# Lista todos os produtos cadastrados.
def produto_list(request):
    produtos = Produto.objects.all()
    return render(request, "produto/list.html", {"produtos": produtos})


# Mostra os detalhes de um produto específico.
def produto_detail(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    return render(request, "produto/detail.html", {"produto": produto})


# Exibe o formulário (GET) e cria um novo produto (POST).
# Usa request.FILES porque o form tem upload de imagem.
def produto_create(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            return redirect("produto_detail", pk=produto.pk)
    else:
        form = ProdutoForm()
    return render(request, "produto/form.html", {"form": form})


# Exibe o formulário pré-preenchido (GET) e salva as alterações (POST),
# incluindo troca de imagem.
def produto_update(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect("produto_detail", pk=produto.pk)
    else:
        form = ProdutoForm(instance=produto)
    return render(request, "produto/form.html", {"form": form})


# Pede confirmação (GET) e exclui o produto (POST).
def produto_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == "POST":
        produto.delete()
        return redirect("produto_list")
    return render(request, "produto/confirm_delete.html", {"produto": produto})

# =============================================================================
# PEDIDO
# =============================================================================

# Form de Pedido: só cliente e status — "criado_em" é preenchido
# automaticamente pelo model (auto_now_add) e não entra no form.
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["cliente", "status"]


# Lista todos os pedidos cadastrados.
def pedido_list(request):
    pedidos = Pedido.objects.all()
    return render(request, "pedido/list.html", {"pedidos": pedidos})


# Mostra os detalhes de um pedido específico.
def pedido_detail(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    return render(request, "pedido/detail.html", {"pedido": pedido})


# Exibe o formulário (GET) e cria um novo pedido (POST).
def pedido_create(request):
    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            return redirect("pedido_detail", pk=pedido.pk)
    else:
        form = PedidoForm()
    return render(request, "pedido/form.html", {"form": form})


# Exibe o formulário pré-preenchido (GET) e salva as alterações (POST).
def pedido_update(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == "POST":
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect("pedido_detail", pk=pedido.pk)
    else:
        form = PedidoForm(instance=pedido)
    return render(request, "pedido/form.html", {"form": form})


# Pede confirmação (GET) e exclui o pedido (POST).
def pedido_delete(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == "POST":
        pedido.delete()
        return redirect("pedido_list")
    return render(request, "pedido/confirm_delete.html", {"pedido": pedido})


# =============================================================================
# ITEMPEDIDO
# =============================================================================

# Form de ItemPedido: a qual pedido pertence, qual produto e a quantidade.
class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ["pedido", "produto", "quantidade"]


# Lista todos os itens de pedido cadastrados.
def itempedido_list(request):
    itens = ItemPedido.objects.all()
    return render(request, "itempedido/list.html", {"itens": itens})


# Mostra os detalhes de um item de pedido específico.
def itempedido_detail(request, pk):
    item = get_object_or_404(ItemPedido, pk=pk)
    return render(request, "itempedido/detail.html", {"item": item})


# Exibe o formulário (GET) e cria um novo item de pedido (POST).
def itempedido_create(request):
    if request.method == "POST":
        form = ItemPedidoForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("itempedido_detail", pk=item.pk)
    else:
        form = ItemPedidoForm()
    return render(request, "itempedido/form.html", {"form": form})


# Exibe o formulário pré-preenchido (GET) e salva as alterações (POST).
def itempedido_update(request, pk):
    item = get_object_or_404(ItemPedido, pk=pk)
    if request.method == "POST":
        form = ItemPedidoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("itempedido_detail", pk=item.pk)
    else:
        form = ItemPedidoForm(instance=item)
    return render(request, "itempedido/form.html", {"form": form})


# Pede confirmação (GET) e exclui o item de pedido (POST).
def itempedido_delete(request, pk):
    item = get_object_or_404(ItemPedido, pk=pk)
    if request.method == "POST":
        item.delete()
        return redirect("itempedido_list")
    return render(request, "itempedido/confirm_delete.html", {"item": item})
