from django.test import TestCase

from companies.models import Company
from transactions.models import CPF_SIZE, DESCRIPTION_LENGTH, Transaction
from transactions.tests.factories import (
    MAX_VALUE,
    MIN_VALUE,
    TransactionFactory,
)


class TestFactories(TestCase):
    def test_transaction_factory(self):
        """
        Should successfully get an instance of Transaction with populated
        attributes
        """
        transaction = TransactionFactory()
        self.assertIsInstance(transaction, Transaction)
        self.assertIsInstance(transaction.company, Company)
        self.assertIsInstance(transaction.client, str)
        self.assertEqual(len(transaction.client), CPF_SIZE)
        self.assertIsInstance(transaction.value, float)
        self.assertGreaterEqual(transaction.value, MIN_VALUE)
        self.assertLessEqual(transaction.value, MAX_VALUE)
        self.assertIsInstance(transaction.description, str)
        self.assertLessEqual(len(transaction.description), DESCRIPTION_LENGTH)
