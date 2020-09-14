from django.urls import reverse

from companies.api.serializers import CompanyReportSerializer
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.api.serializers import (
    TransactionReportSerializer,
    TransactionSerializer,
)
from transactions.models import Transaction
from transactions.tests.factories import TransactionFactory

TRANSACTION_VIEW_NAME = "v1:transaction"
REPORT_VIEW_NAME = "v1:report"


class TestTransactionEndpoint(APITestCase):
    def test_transaction_creation(self):
        """
        Should successfully create a Transaction record in the database when
        POSTing to the endpoint, returning HTTP Status 201 and the expected
        message
        """
        url = reverse(TRANSACTION_VIEW_NAME)
        transaction = TransactionFactory.build()
        transaction.company.save()
        payload = TransactionSerializer(transaction).data

        self.assertEqual(Transaction.objects.count(), 0)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"aceito": True})
        self.assertEqual(Transaction.objects.count(), 1)

    def test_transaction_creation_company_does_not_exist(self):
        """
        Should fail to create a Transaction record in the database when
        POSTing to the endpoint with a company cnpj that does not exist in
        the database, returning HTTP Status 404 and the expected message
        """
        url = reverse(TRANSACTION_VIEW_NAME)
        transaction = TransactionFactory.build()
        payload = TransactionSerializer(transaction).data

        self.assertEqual(Transaction.objects.count(), 0)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"aceito": False})
        self.assertEqual(Transaction.objects.count(), 0)

    def test_transaction_creation_invalid_client(self):
        """
        Should fail to create a Transaction record in the database when
        POSTing to the endpoint with an invalid client cpf, returning
        HTTP Status 400 and the expected message
        """
        url = reverse(TRANSACTION_VIEW_NAME)
        transaction = TransactionFactory.build()
        transaction.company.save()
        payload = TransactionSerializer(transaction).data
        payload["cliente"] = 100

        self.assertEqual(Transaction.objects.count(), 0)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"aceito": False})
        self.assertEqual(Transaction.objects.count(), 0)

    def test_transaction_creation_invalid_value(self):
        """
        Should fail to create a Transaction record in the database when
        POSTing to the endpoint with an invalid value, returning
        HTTP Status 400 and the expected message
        """
        url = reverse(TRANSACTION_VIEW_NAME)
        transaction = TransactionFactory.build()
        transaction.company.save()
        payload = TransactionSerializer(transaction).data
        payload["valor"] = "invalid"

        self.assertEqual(Transaction.objects.count(), 0)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"aceito": False})
        self.assertEqual(Transaction.objects.count(), 0)


class TestReportEndpoint(APITestCase):
    def test_report_missing_cnpj(self):
        """
        Should fail to get a transactions report when GETting the endpoint
        but missing the cnpj parameter in the query string, returning HTTP
        Status 400 and the expected message
        """
        url = reverse(REPORT_VIEW_NAME)

        expected_message = (
            "O parametro obrigatorio 'cnpj' nao foi incluido na query string"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"erro": expected_message})

    def test_report_invalid_cnpj(self):
        """
        Should fail to get a transactions report when GETting the endpoint
        and providing an invalid cnpj parameter in the query string,
        returning HTTP Status 400 and the expected message
        """
        url = reverse(REPORT_VIEW_NAME)
        invalid_cnpj = "11.111.111/1111-11"

        expected_message = "Informe um 'cnpj' valido"
        response = self.client.get(url, {"cnpj": invalid_cnpj})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"erro": expected_message})

    def test_report_company_not_found(self):
        """
        Should fail to get a transactions report when GETting the endpoint
        and providing a cnpj of a company that is not in the database,
        returning HTTP Status 404 and the expected message
        """
        url = reverse(REPORT_VIEW_NAME)
        transaction = TransactionFactory.build()
        cnpj = transaction.company.cnpj

        expected_message = f"Estabelecimento com cnpj '{cnpj}' nao encontrado"
        response = self.client.get(url, {"cnpj": cnpj})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"erro": expected_message})

    def test_report(self):
        """
        Should successfully get a transactions report when GETting the
        endpoint providing a company cnpj that is in the database,
        returning HTTP Status 200 and the expected data
        """
        transaction_one = TransactionFactory.build()
        transaction_one.company.save()
        transaction_one.save()
        transaction_two = TransactionFactory.build()
        transaction_two.company = transaction_one.company
        transaction_two.save()
        company = transaction_one.company

        expected_data = {
            "estabelecimento": CompanyReportSerializer(company).data,
            "recebimentos": [
                TransactionReportSerializer(transaction_one).data,
                TransactionReportSerializer(transaction_two).data,
            ],
            "total_recebido": transaction_one.value + transaction_two.value,
        }

        url = reverse(REPORT_VIEW_NAME)
        cnpj = company.cnpj

        response = self.client.get(url, {"cnpj": cnpj})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_report_no_transactions(self):
        """
        Should successfully get a transactions report when GETting the
        endpoint providing a company cnpj that is in the database but has
        no transactions, returning HTTP Status 200 and the expected data
        """
        transaction = TransactionFactory.build()
        transaction.company.save()
        company = transaction.company

        expected_data = {
            "estabelecimento": CompanyReportSerializer(company).data,
            "recebimentos": [],
            "total_recebido": 0.00,
        }

        url = reverse(REPORT_VIEW_NAME)
        cnpj = company.cnpj

        response = self.client.get(url, {"cnpj": cnpj})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
