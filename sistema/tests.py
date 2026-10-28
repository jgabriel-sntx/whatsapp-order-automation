from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from .models import Cadastro, Categoria, Cliente, Empresa, ItemPedido, Pedido, Produto


class ModelsTest(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(username="pizzaria", nome="Pizzaria", telefone="1", endereco="Rua 1")
        self.categoria = Categoria.objects.create(empresa=self.empresa, nome="Pizzas")
        self.produto = Produto.objects.create(categoria=self.categoria, nome="Calabresa", preco=Decimal("10"))
        self.cliente = Cliente.objects.create(nome="Maria", telefone="1", endereco="Rua X")
        self.cliente.empresa.add(self.empresa)
        self.pedido = Pedido.objects.create(cliente=self.cliente)

    def test_preco_negativo_invalido(self):
        produto = Produto(categoria=self.categoria, nome="X", preco=Decimal("-5"))
        with self.assertRaises(ValidationError):
            produto.full_clean()

    def test_quantidade_zero_invalida(self):
        item = ItemPedido(pedido=self.pedido, produto=self.produto, quantidade=0)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_cadastro_duplicado_bloqueado(self):
        with self.assertRaises(IntegrityError):
            Cadastro.objects.create(empresa=self.empresa, cliente=self.cliente)

    def test_produto_em_pedido_nao_pode_ser_apagado(self):
        ItemPedido.objects.create(pedido=self.pedido, produto=self.produto, quantidade=2)
        with self.assertRaises(ProtectedError):
            self.produto.delete()

    def test_total_do_pedido(self):
        ItemPedido.objects.create(pedido=self.pedido, produto=self.produto, quantidade=3)
        self.assertEqual(self.pedido.calcular_total(), Decimal("30"))


class AdminTest(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser("admin", "a@a.com", "senha123")
        self.client.force_login(admin)

    def test_models_registrados_no_admin(self):
        for url in ["/admin/sistema/categoria/", "/admin/sistema/cadastro/", "/admin/sistema/empresa/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
