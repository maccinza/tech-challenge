from companies.models import Company
from rest_framework import serializers
from transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    estabelecimento = serializers.CharField(source="company.cnpj")
    cliente = serializers.CharField(source="client")
    valor = serializers.FloatField(source="value")
    descricao = serializers.CharField(source="description")

    class Meta:
        model = Transaction
        fields = ["estabelecimento", "cliente", "valor", "descricao"]


class WritableTransactionSerializer(serializers.ModelSerializer):
    estabelecimento = serializers.PrimaryKeyRelatedField(
        source="company", queryset=Company.objects.all()
    )
    cliente = serializers.CharField(source="client")
    valor = serializers.FloatField(source="value")
    descricao = serializers.CharField(source="description")

    class Meta:
        model = Transaction
        fields = ["estabelecimento", "cliente", "valor", "descricao"]
