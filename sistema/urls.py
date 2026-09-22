from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # Empresa: CRUD completo.
    path("empresas/", views.empresa_list, name="empresa_list"),
    path("empresas/nova/", views.empresa_create, name="empresa_create"),
    path("empresas/<int:pk>/", views.empresa_detail, name="empresa_detail"),
    path("empresas/<int:pk>/editar/", views.empresa_update, name="empresa_update"),
    path("empresas/<int:pk>/excluir/", views.empresa_delete, name="empresa_delete"),

    # Categoria: CRUD completo.
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nova/", views.categoria_create, name="categoria_create"),
    path("categorias/<int:pk>/", views.categoria_detail, name="categoria_detail"),
    path("categorias/<int:pk>/editar/", views.categoria_update, name="categoria_update"),
    path("categorias/<int:pk>/excluir/", views.categoria_delete, name="categoria_delete"),
    
    # Cliente: CRUD completo.
    path("clientes/", views.cliente_list, name="cliente_list"),
    path("clientes/novo/", views.cliente_create, name="cliente_create"),
    path("clientes/<int:pk>/", views.cliente_detail, name="cliente_detail"),
    path("clientes/<int:pk>/editar/", views.cliente_update, name="cliente_update"),
    path("clientes/<int:pk>/excluir/", views.cliente_delete, name="cliente_delete"),

    # Produto: CRUD completo.
    path("produtos/", views.produto_list, name="produto_list"),
    path("produtos/novo/", views.produto_create, name="produto_create"),
    path("produtos/<int:pk>/", views.produto_detail, name="produto_detail"),
    path("produtos/<int:pk>/editar/", views.produto_update, name="produto_update"),
    path("produtos/<int:pk>/excluir/", views.produto_delete, name="produto_delete"),
]