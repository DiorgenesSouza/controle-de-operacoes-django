from django.db import models


class Operacao(models.Model):
    STATUS_CHOICES = [
        ("Em trânsito", "Em trânsito"),
        ("Entregue", "Entregue"),
    ]

    TIPO_CHOICES = [
        ("Operação fora de CD", "Operação fora de CD"),
        ("Coleta", "Coleta"),
        ("Transferência", "Transferência"),
        ("Entrega direta", "Entrega direta"),
        ("Outro", "Outro"),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    numero_nota = models.CharField(max_length=50)
    valor_nota = models.DecimalField(max_digits=18, decimal_places=2)
    cliente = models.CharField(max_length=150)
    origem = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)

    tipo_operacao = models.CharField(
        max_length=100,
        choices=TIPO_CHOICES
    )

    data_recebimento = models.DateField()

    status_operacao = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Em trânsito"
    )

    placa = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    motorista = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    data_entrega = models.DateTimeField(
        blank=True,
        null=True
    )

    ativo = models.BooleanField(default=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo} - NF {self.numero_nota}"