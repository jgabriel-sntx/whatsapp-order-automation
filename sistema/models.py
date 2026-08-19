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


