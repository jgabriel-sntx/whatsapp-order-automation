from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    PEDIDO_STATUS_FECHADOS,
    CategoriaForm,
    ClienteForm,
    EmpresaCreateForm,
    EmpresaForm,
    ItemPedidoForm,
    PedidoForm,
    ProdutoForm,
)
from .models import Cadastro, Categoria, Cliente, Empresa, ItemPedido, Pedido, Produto

MSG_FORM_INVALIDO = "Não foi possível salvar. Corrija os erros abaixo."


# =============================================================================
# AUTENTICAÇÃO E ESCOPO POR EMPRESA
# =============================================================================

# Exige login E que o usuário logado seja uma Empresa (e não, por exemplo, um
# superusuário do admin). Guarda a empresa em request.empresa para as views.
def empresa_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            request.empresa = request.user.empresa
        except Empresa.DoesNotExist:
            raise PermissionDenied("Este usuário não está ligado a uma empresa.")
        return view(request, *args, **kwargs)

    return wrapper


# Querysets já filtrados pela empresa logada. Toda busca por pk passa por
# eles, então um registro de outra empresa devolve 404.
def categorias_da_empresa(empresa):
    return Categoria.objects.filter(empresa=empresa)


def clientes_da_empresa(empresa):
    return Cliente.objects.filter(empresa=empresa)


def produtos_da_empresa(empresa):
    return Produto.objects.filter(categoria__empresa=empresa)


def pedidos_da_empresa(empresa):
    return Pedido.objects.filter(cliente__empresa=empresa)


def itens_da_empresa(empresa):
    return ItemPedido.objects.filter(pedido__cliente__empresa=empresa)


# Página inicial com o menu de navegação (definido em base.html).
@empresa_required
def index(request):
    return render(request, "index.html")


# =============================================================================
# EMPRESA
# =============================================================================

# Cada empresa só enxerga a si mesma.
@empresa_required
def empresa_list(request):
    empresas = Empresa.objects.filter(pk=request.empresa.pk)
    return render(request, "empresa/list.html", {"empresas": empresas})


@empresa_required
def empresa_detail(request, pk):
    empresa = get_object_or_404(Empresa.objects.filter(pk=request.empresa.pk), pk=pk)
    return render(request, "empresa/detail.html", {"empresa": empresa})


# Cadastro público de empresa (sem login): cria User + Empresa de uma vez e
# manda para a tela de login.
def empresa_create(request):
    if request.method == "POST":
        form = EmpresaCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa cadastrada com sucesso. Faça login para continuar.")
            return redirect("login")
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = EmpresaCreateForm()
    return render(request, "empresa/form.html", {"form": form})


@empresa_required
def empresa_update(request, pk):
    empresa = get_object_or_404(Empresa.objects.filter(pk=request.empresa.pk), pk=pk)
    if request.method == "POST":
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa atualizada com sucesso.")
            return redirect("empresa_detail", pk=empresa.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, "empresa/form.html", {"form": form})


# Excluir a empresa apaga a própria conta, então encerra a sessão em seguida.
@empresa_required
def empresa_delete(request, pk):
    empresa = get_object_or_404(Empresa.objects.filter(pk=request.empresa.pk), pk=pk)
    if request.method == "POST":
        try:
            empresa.delete()
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir a empresa enquanto houver produtos cadastrados em suas categorias.",
            )
            return redirect("empresa_detail", pk=empresa.pk)
        logout(request)
        messages.success(request, "Empresa excluída com sucesso.")
        return redirect("login")
    return render(request, "empresa/confirm_delete.html", {"empresa": empresa})


# =============================================================================
# CATEGORIA
# =============================================================================

@empresa_required
def categoria_list(request):
    categorias = categorias_da_empresa(request.empresa)
    return render(request, "categoria/list.html", {"categorias": categorias})


@empresa_required
def categoria_detail(request, pk):
    categoria = get_object_or_404(categorias_da_empresa(request.empresa), pk=pk)
    return render(request, "categoria/detail.html", {"categoria": categoria})


@empresa_required
def categoria_create(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.empresa = request.empresa
            categoria.save()
            messages.success(request, "Categoria criada com sucesso.")
            return redirect("categoria_detail", pk=categoria.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = CategoriaForm()
    return render(request, "categoria/form.html", {"form": form})


@empresa_required
def categoria_update(request, pk):
    categoria = get_object_or_404(categorias_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso.")
            return redirect("categoria_detail", pk=categoria.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, "categoria/form.html", {"form": form})


@empresa_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(categorias_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        try:
            categoria.delete()
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir esta categoria porque ela possui produtos cadastrados.",
            )
            return redirect("categoria_detail", pk=categoria.pk)
        messages.success(request, "Categoria excluída com sucesso.")
        return redirect("categoria_list")
    return render(request, "categoria/confirm_delete.html", {"categoria": categoria})


# =============================================================================
# CLIENTE
# =============================================================================

@empresa_required
def cliente_list(request):
    clientes = clientes_da_empresa(request.empresa)
    return render(request, "cliente/list.html", {"clientes": clientes})


@empresa_required
def cliente_detail(request, pk):
    cliente = get_object_or_404(clientes_da_empresa(request.empresa), pk=pk)
    return render(request, "cliente/detail.html", {"cliente": cliente})


# Cria o cliente e o Cadastro (tabela de ligação) com a empresa logada,
# na mesma transação: ou grava os dois ou nenhum.
@empresa_required
def cliente_create(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                cliente = form.save()
                Cadastro.objects.create(empresa=request.empresa, cliente=cliente)
            messages.success(request, "Cliente criado com sucesso.")
            return redirect("cliente_detail", pk=cliente.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ClienteForm()
    return render(request, "cliente/form.html", {"form": form})


@empresa_required
def cliente_update(request, pk):
    cliente = get_object_or_404(clientes_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente atualizado com sucesso.")
            return redirect("cliente_detail", pk=cliente.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "cliente/form.html", {"form": form})


@empresa_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(clientes_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        try:
            cliente.delete()
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir este cliente porque ele possui pedidos cadastrados.",
            )
            return redirect("cliente_detail", pk=cliente.pk)
        messages.success(request, "Cliente excluído com sucesso.")
        return redirect("cliente_list")
    return render(request, "cliente/confirm_delete.html", {"cliente": cliente})


# =============================================================================
# PRODUTO
# =============================================================================

@empresa_required
def produto_list(request):
    produtos = produtos_da_empresa(request.empresa)
    return render(request, "produto/list.html", {"produtos": produtos})


@empresa_required
def produto_detail(request, pk):
    produto = get_object_or_404(produtos_da_empresa(request.empresa), pk=pk)
    return render(request, "produto/detail.html", {"produto": produto})


# Usa request.FILES porque o form tem upload de imagem.
@empresa_required
def produto_create(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, empresa=request.empresa)
        if form.is_valid():
            produto = form.save()
            messages.success(request, "Produto criado com sucesso.")
            return redirect("produto_detail", pk=produto.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ProdutoForm(empresa=request.empresa)
    return render(request, "produto/form.html", {"form": form})


@empresa_required
def produto_update(request, pk):
    produto = get_object_or_404(produtos_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto, empresa=request.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado com sucesso.")
            return redirect("produto_detail", pk=produto.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ProdutoForm(instance=produto, empresa=request.empresa)
    return render(request, "produto/form.html", {"form": form})


@empresa_required
def produto_delete(request, pk):
    produto = get_object_or_404(produtos_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        try:
            produto.delete()
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir este produto porque ele está em itens de pedido.",
            )
            return redirect("produto_detail", pk=produto.pk)
        messages.success(request, "Produto excluído com sucesso.")
        return redirect("produto_list")
    return render(request, "produto/confirm_delete.html", {"produto": produto})


# =============================================================================
# PEDIDO
# =============================================================================

@empresa_required
def pedido_list(request):
    pedidos = pedidos_da_empresa(request.empresa)
    return render(request, "pedido/list.html", {"pedidos": pedidos})


@empresa_required
def pedido_detail(request, pk):
    pedido = get_object_or_404(pedidos_da_empresa(request.empresa), pk=pk)
    return render(request, "pedido/detail.html", {"pedido": pedido})


@empresa_required
def pedido_create(request):
    if request.method == "POST":
        form = PedidoForm(request.POST, empresa=request.empresa)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, "Pedido criado com sucesso.")
            return redirect("pedido_detail", pk=pedido.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = PedidoForm(empresa=request.empresa)
    return render(request, "pedido/form.html", {"form": form})


@empresa_required
def pedido_update(request, pk):
    pedido = get_object_or_404(pedidos_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        form = PedidoForm(request.POST, instance=pedido, empresa=request.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Pedido atualizado com sucesso.")
            return redirect("pedido_detail", pk=pedido.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = PedidoForm(instance=pedido, empresa=request.empresa)
    return render(request, "pedido/form.html", {"form": form})


@empresa_required
def pedido_delete(request, pk):
    pedido = get_object_or_404(pedidos_da_empresa(request.empresa), pk=pk)
    if request.method == "POST":
        pedido.delete()
        messages.success(request, "Pedido excluído com sucesso.")
        return redirect("pedido_list")
    return render(request, "pedido/confirm_delete.html", {"pedido": pedido})


# =============================================================================
# ITEMPEDIDO
# =============================================================================

# Se o pedido do item está cancelado/finalizado, avisa o usuário e devolve
# True para a view interromper a operação.
def _pedido_do_item_fechado(request, item, acao):
    pedido = item.pedido
    if pedido.status in PEDIDO_STATUS_FECHADOS:
        messages.error(
            request,
            f"Não é possível {acao} itens de um pedido {pedido.get_status_display().lower()}.",
        )
        return True
    return False


@empresa_required
def itempedido_list(request):
    itens = itens_da_empresa(request.empresa)
    return render(request, "itempedido/list.html", {"itens": itens})


@empresa_required
def itempedido_detail(request, pk):
    item = get_object_or_404(itens_da_empresa(request.empresa), pk=pk)
    return render(request, "itempedido/detail.html", {"item": item})


# O ItemPedidoForm já recusa pedido cancelado/finalizado (clean_pedido).
@empresa_required
def itempedido_create(request):
    if request.method == "POST":
        form = ItemPedidoForm(request.POST, empresa=request.empresa)
        if form.is_valid():
            item = form.save()
            messages.success(request, "Item adicionado com sucesso.")
            return redirect("itempedido_detail", pk=item.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ItemPedidoForm(empresa=request.empresa)
    return render(request, "itempedido/form.html", {"form": form})


@empresa_required
def itempedido_update(request, pk):
    item = get_object_or_404(itens_da_empresa(request.empresa), pk=pk)
    if _pedido_do_item_fechado(request, item, "alterar"):
        return redirect("itempedido_detail", pk=item.pk)
    if request.method == "POST":
        form = ItemPedidoForm(request.POST, instance=item, empresa=request.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Item atualizado com sucesso.")
            return redirect("itempedido_detail", pk=item.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ItemPedidoForm(instance=item, empresa=request.empresa)
    return render(request, "itempedido/form.html", {"form": form})


@empresa_required
def itempedido_delete(request, pk):
    item = get_object_or_404(itens_da_empresa(request.empresa), pk=pk)
    if _pedido_do_item_fechado(request, item, "excluir"):
        return redirect("itempedido_detail", pk=item.pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item excluído com sucesso.")
        return redirect("itempedido_list")
    return render(request, "itempedido/confirm_delete.html", {"item": item})