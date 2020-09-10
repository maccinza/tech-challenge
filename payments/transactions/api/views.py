from copy import deepcopy

from companies.models import Company
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from transactions.api.serializers import (
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
