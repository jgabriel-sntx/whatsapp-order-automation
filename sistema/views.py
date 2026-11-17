from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

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

# Permissões nativas do Django (app.acao_model) dadas a toda empresa nova, no
# cadastro. Cada view confere uma delas com @permission_required.
_MODELOS_COM_CRUD = ("categoria", "cliente", "produto", "pedido", "itempedido")
PERMISSOES_EMPRESA = ["view_empresa", "change_empresa", "delete_empresa"] + [
    f"{acao}_{modelo}"
    for modelo in _MODELOS_COM_CRUD
    for acao in ("add", "change", "delete", "view")
]


# Querysets já filtrados pela empresa logada. Toda busca por pk passa por
# eles, então um registro de outra empresa devolve 404.
def categorias_da_empresa(empresa):
    return Categoria.objects.filter(empresa=empresa)


def clientes_da_empresa(empresa):
    return Cliente.objects.filter(empresa=empresa)


def produtos_da_empresa(empresa):
    return Produto.objects.filter(categoria__empresa=empresa).select_related("categoria")


def pedidos_da_empresa(empresa):
    return Pedido.objects.filter(cliente__empresa=empresa).select_related("cliente")


def itens_da_empresa(empresa):
    return ItemPedido.objects.filter(pedido__cliente__empresa=empresa).select_related(
        "pedido", "produto"
    )


# =============================================================================
# LOGIN E LOGOUT (FBV)
# =============================================================================

# Login em FBV usando o formulário pronto do Django (AuthenticationForm).
# O parâmetro "next" só é seguido se apontar para este mesmo site.
def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    proximo = request.POST.get("next") or request.GET.get("next", "")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Login realizado com sucesso.")
            if url_has_allowed_host_and_scheme(
                proximo, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(proximo)
            return redirect("index")
        messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm(request)
    return render(request, "registration/login.html", {"form": form, "next": proximo})


# Só aceita POST (o botão "Sair" do menu é um formulário com CSRF).
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu do sistema.")
    return redirect("login")


# Página inicial com o menu de navegação (definido em base.html).

# =============================================================================
# EMPRESA
# =============================================================================

# Cada empresa só enxerga a si mesma.
@login_required
@permission_required("sistema.view_empresa", raise_exception=True)
def empresa_list(request):
    empresas = Empresa.objects.filter(pk=request.user.empresa.pk)
    return render(request, "empresa/list.html", {"empresas": empresas})

@login_required
@permission_required("sistema.view_empresa", raise_exception=True)
def empresa_detail(request, pk):
    empresa = get_object_or_404(Empresa.objects.filter(pk=request.user.empresa.pk), pk=pk)
    return render(request, "empresa/detail.html", {"empresa": empresa})


# Cadastro público de empresa (sem login): cria User + Empresa de uma vez e
# manda para a tela de login.
def empresa_create(request):
    if request.method == "POST":
        form = EmpresaCreateForm(request.POST)
        if form.is_valid():
            empresa = form.save()
            empresa.user_permissions.set(
                Permission.objects.filter(
                    content_type__app_label="sistema", codename__in=PERMISSOES_EMPRESA
                )
            )
            messages.success(request, "Empresa cadastrada com sucesso. Faça login para continuar.")
            return redirect("login")
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = EmpresaCreateForm()
    return render(request, "empresa/form.html", {"form": form})

@login_required
@permission_required("sistema.change_empresa", raise_exception=True)
def empresa_update(request, pk):
    empresa = get_object_or_404(Empresa.objects.filter(pk=request.user.empresa.pk), pk=pk)
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
@login_required
@permission_required("sistema.delete_empresa", raise_exception=True)
def empresa_delete(request, pk):
    empresa = get_object_or_404(Empresa.objects.filter(pk=request.user.empresa.pk), pk=pk)
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

@login_required
@permission_required("sistema.view_categoria", raise_exception=True)
def categoria_list(request):
    categorias = categorias_da_empresa(request.user.empresa)
    return render(request, "categoria/list.html", {"categorias": categorias})


@login_required
@permission_required("sistema.view_categoria", raise_exception=True)
def categoria_detail(request, pk):
    categoria = get_object_or_404(categorias_da_empresa(request.user.empresa), pk=pk)
    return render(request, "categoria/detail.html", {"categoria": categoria})


@login_required
@permission_required("sistema.add_categoria", raise_exception=True)
def categoria_create(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.empresa = request.user.empresa
            categoria.save()
            messages.success(request, "Categoria criada com sucesso.")
            return redirect("categoria_detail", pk=categoria.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = CategoriaForm()
    return render(request, "categoria/form.html", {"form": form})

@login_required
@permission_required("sistema.change_categoria", raise_exception=True)
def categoria_update(request, pk):
    categoria = get_object_or_404(categorias_da_empresa(request.user.empresa), pk=pk)
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

@login_required
@permission_required("sistema.delete_categoria", raise_exception=True)
def categoria_delete(request, pk):
    categoria = get_object_or_404(categorias_da_empresa(request.user.empresa), pk=pk)
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

@login_required
@permission_required("sistema.view_cliente", raise_exception=True)
def cliente_list(request):
    clientes = clientes_da_empresa(request.user.empresa)
    return render(request, "cliente/list.html", {"clientes": clientes})


@login_required
@permission_required("sistema.view_cliente", raise_exception=True)
def cliente_detail(request, pk):
    cliente = get_object_or_404(clientes_da_empresa(request.user.empresa), pk=pk)
    return render(request, "cliente/detail.html", {"cliente": cliente})


# Cria o cliente e o Cadastro (tabela de ligação) com a empresa logada,
# na mesma transação: ou grava os dois ou nenhum.
@login_required
@permission_required("sistema.add_cliente", raise_exception=True)
def cliente_create(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                cliente = form.save()
                Cadastro.objects.create(empresa=request.user.empresa, cliente=cliente)
            messages.success(request, "Cliente criado com sucesso.")
            return redirect("cliente_detail", pk=cliente.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ClienteForm()
    return render(request, "cliente/form.html", {"form": form})


@login_required
@permission_required("sistema.change_cliente", raise_exception=True)
def cliente_update(request, pk):
    cliente = get_object_or_404(clientes_da_empresa(request.user.empresa), pk=pk)
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


@login_required
@permission_required("sistema.delete_cliente", raise_exception=True)
def cliente_delete(request, pk):
    cliente = get_object_or_404(clientes_da_empresa(request.user.empresa), pk=pk)
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

@login_required
@permission_required("sistema.view_produto", raise_exception=True)
def produto_list(request):
    produtos = produtos_da_empresa(request.user.empresa)
    return render(request, "produto/list.html", {"produtos": produtos})


@login_required
@permission_required("sistema.view_produto", raise_exception=True)
def produto_detail(request, pk):
    produto = get_object_or_404(produtos_da_empresa(request.user.empresa), pk=pk)
    return render(request, "produto/detail.html", {"produto": produto})


# Usa request.FILES porque o form tem upload de imagem.
@login_required
@permission_required("sistema.add_produto", raise_exception=True)
def produto_create(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, empresa=request.user.empresa)
        if form.is_valid():
            produto = form.save()
            messages.success(request, "Produto criado com sucesso.")
            return redirect("produto_detail", pk=produto.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ProdutoForm(empresa=request.user.empresa)
    return render(request, "produto/form.html", {"form": form})


@login_required
@permission_required("sistema.change_produto", raise_exception=True)
def produto_update(request, pk):
    produto = get_object_or_404(produtos_da_empresa(request.user.empresa), pk=pk)
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto, empresa=request.user.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado com sucesso.")
            return redirect("produto_detail", pk=produto.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ProdutoForm(instance=produto, empresa=request.user.empresa)
    return render(request, "produto/form.html", {"form": form})


@login_required
@permission_required("sistema.delete_produto", raise_exception=True)
def produto_delete(request, pk):
    produto = get_object_or_404(produtos_da_empresa(request.user.empresa), pk=pk)
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

@login_required
@permission_required("sistema.view_pedido", raise_exception=True)
def pedido_list(request):
    pedidos = pedidos_da_empresa(request.user.empresa)
    return render(request, "pedido/list.html", {"pedidos": pedidos})


@login_required
@permission_required("sistema.view_pedido", raise_exception=True)
def pedido_detail(request, pk):
    pedidos = pedidos_da_empresa(request.user.empresa).prefetch_related("itens__produto")
    pedido = get_object_or_404(pedidos, pk=pk)
    return render(request, "pedido/detail.html", {"pedido": pedido})


@login_required
@permission_required("sistema.add_pedido", raise_exception=True)
def pedido_create(request):
    if request.method == "POST":
        form = PedidoForm(request.POST, empresa=request.user.empresa)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, "Pedido criado com sucesso.")
            return redirect("pedido_detail", pk=pedido.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = PedidoForm(empresa=request.user.empresa)
    return render(request, "pedido/form.html", {"form": form})


@login_required
@permission_required("sistema.change_pedido", raise_exception=True)
def pedido_update(request, pk):
    pedido = get_object_or_404(pedidos_da_empresa(request.user.empresa), pk=pk)
    if request.method == "POST":
        form = PedidoForm(request.POST, instance=pedido, empresa=request.user.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Pedido atualizado com sucesso.")
            return redirect("pedido_detail", pk=pedido.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = PedidoForm(instance=pedido, empresa=request.user.empresa)
    return render(request, "pedido/form.html", {"form": form})


@login_required
@permission_required("sistema.delete_pedido", raise_exception=True)
def pedido_delete(request, pk):
    pedido = get_object_or_404(pedidos_da_empresa(request.user.empresa), pk=pk)
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


@login_required
@permission_required("sistema.view_itempedido", raise_exception=True)
def itempedido_list(request):
    itens = itens_da_empresa(request.user.empresa)
    return render(request, "itempedido/list.html", {"itens": itens})


@login_required
@permission_required("sistema.view_itempedido", raise_exception=True)
def itempedido_detail(request, pk):
    item = get_object_or_404(itens_da_empresa(request.user.empresa), pk=pk)
    return render(request, "itempedido/detail.html", {"item": item})


# O ItemPedidoForm já recusa pedido cancelado/finalizado (clean_pedido).
@login_required
@permission_required("sistema.add_itempedido", raise_exception=True)
def itempedido_create(request):
    if request.method == "POST":
        form = ItemPedidoForm(request.POST, empresa=request.user.empresa)
        if form.is_valid():
            item = form.save()
            messages.success(request, "Item adicionado com sucesso.")
            return redirect("itempedido_detail", pk=item.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ItemPedidoForm(empresa=request.user.empresa)
    return render(request, "itempedido/form.html", {"form": form})


@login_required
@permission_required("sistema.change_itempedido", raise_exception=True)
def itempedido_update(request, pk):
    item = get_object_or_404(itens_da_empresa(request.user.empresa), pk=pk)
    if _pedido_do_item_fechado(request, item, "alterar"):
        return redirect("itempedido_detail", pk=item.pk)
    if request.method == "POST":
        form = ItemPedidoForm(request.POST, instance=item, empresa=request.user.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Item atualizado com sucesso.")
            return redirect("itempedido_detail", pk=item.pk)
        messages.error(request, MSG_FORM_INVALIDO)
    else:
        form = ItemPedidoForm(instance=item, empresa=request.user.empresa)
    return render(request, "itempedido/form.html", {"form": form})


@login_required
@permission_required("sistema.delete_itempedido", raise_exception=True)
def itempedido_delete(request, pk):
    item = get_object_or_404(itens_da_empresa(request.user.empresa), pk=pk)
    if _pedido_do_item_fechado(request, item, "excluir"):
        return redirect("itempedido_detail", pk=item.pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item excluído com sucesso.")
        return redirect("itempedido_list")
    return render(request, "itempedido/confirm_delete.html", {"item": item})