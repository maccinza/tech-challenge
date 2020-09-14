from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from transactions.api.serializers import TransactionSerializer
from transactions.models import Transaction
from transactions.tests.factories import TransactionFactory

TRANSACTION_VIEW_NAME = "v1:transaction"


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
