from companies.api.serializers import CompanyReportSerializer
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


class TransactionReportSerializer(TransactionSerializer):
    class Meta:
        model = Transaction
        fields = ["cliente", "valor", "descricao"]


class WritableTransactionSerializer(TransactionSerializer):
    estabelecimento = serializers.PrimaryKeyRelatedField(
        source="company", queryset=Company.objects.all()
    )


class ReportSerializer(serializers.Serializer):
    estabelecimento = serializers.SerializerMethodField("get_company")
    recebimentos = serializers.SerializerMethodField("get_transactions")
    total_recebido = serializers.SerializerMethodField("get_total")

    def get_company(self, instance):
        return CompanyReportSerializer(instance).data

    def get_transactions(self, instance):
        return TransactionReportSerializer(
            instance.transactions.all(), many=True
        ).data

    def get_total(self, instance):
        return getattr(instance, "total_value", 0.00)
