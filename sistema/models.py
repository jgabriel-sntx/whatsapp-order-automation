from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Empresa(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="empresa"
    )
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=255)
    instrucoes_atendimento = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="categorias"
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="clientes"

    )
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=255)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="produtos"
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Pedido(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("confirmado", "Confirmado"),
        ("finalizado", "Finalizado"),
        ("cancelado", "Cancelado"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="pedidos"
    )
    STATUS = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente"
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def calcular_total(self):
        return sum(item.calcular_subtotal() for item in self.itens.all())

    def confirmar(self):
        self.status = "confirmado"
        self.save()

    def finalizar(self):
        self.status = "finalizado"
        self.save()

    def cancelar(self):
        self.status = "cancelado"
        self.save()

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nome}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    quantidade = models.PositiveIntegerField(default=1)

    def calcular_subtotal(self):
        return self.produto.preco * self.quantidade

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade}x {self.pedido.produto.nome}"
