from django import forms
from django.shortcuts import get_object_or_404, redirect, render

from .models import Categoria, Empresa


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
