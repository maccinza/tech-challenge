from copy import deepcopy

from django.db.models import Sum

from companies.models import Company
from pycpfcnpj.cpfcnpj import validate as cnpj_is_valid
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from transactions.api.serializers import (
    ReportSerializer,
    TransactionSerializer,
    WritableTransactionSerializer,
)


class RecordTransactionView(CreateAPIView):
    serializer_class = TransactionSerializer

    def _return_error_response(self, status):
        return Response({"aceito": False}, status=status)

    def create(self, request, *args, **kwargs):
        data = deepcopy(request.data)
        data["estabelecimento"] = kwargs.get("company_id")

        serializer = WritableTransactionSerializer(data=data)
        if not serializer.is_valid():
            self._return_error_response(status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_create(serializer)
        except Exception:
            return self._return_error_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"aceito": True}, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return self._return_error_response(status.HTTP_400_BAD_REQUEST)
        try:
            company = Company.objects.get(
                cnpj=request.data.get("estabelecimento")
            )
        except Company.DoesNotExist:
            return self._return_error_response(status.HTTP_404_NOT_FOUND)

        kwargs.update({"company_id": company.id})
        return self.create(request, *args, **kwargs)


class TransactionsReportView(RetrieveAPIView):
    serializer_class = ReportSerializer

    def _return_error_response(self, status, message):
        return Response({"erro": message}, status=status)

    def retrieve(self, request, *args, **kwargs):
        company = kwargs["company"]
        serializer = self.get_serializer(company)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        http_status = status.HTTP_400_BAD_REQUEST
        cnpj = request.GET.get("cnpj", None)
        if not cnpj:
            message = (
                "O parametro obrigatorio 'cnpj' nao foi incluido "
                "na query string"
            )
            return self._return_error_response(http_status, message)

        elif not cnpj_is_valid(cnpj):
            message = "Informe um 'cnpj' valido"
            return self._return_error_response(http_status, message)

        company = (
            Company.objects.filter(cnpj=cnpj)
            .prefetch_related("transactions")
            .annotate(total_value=Sum("transactions__value"))
            .first()
        )

        if not company:
            message = f"Estabelecimento com cnpj '{cnpj}' nao encontrado"
            http_status = status.HTTP_404_NOT_FOUND
            return self._return_error_response(http_status, message)

        kwargs.update({"company": company})
        return self.retrieve(request, *args, **kwargs)
