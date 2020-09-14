from companies.models import Company
from rest_framework import serializers


class CompanyReportSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source="name")
    cnpj = serializers.CharField()
    dono = serializers.CharField(source="owner")
    telefone = serializers.SerializerMethodField("get_telephone")

    def get_telephone(self, instance):
        return str(instance.full_phone)

    class Meta:
        model = Company
        fields = ["nome", "cnpj", "dono", "telefone"]
