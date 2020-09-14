from django.core.validators import ValidationError
from django.test import TestCase

from transactions.models import CPF_SIZE, Transaction
from transactions.tests.factories import TransactionFactory


class TestTransactionModel(TestCase):
    def test_model_creation(self):
        """
        Should successfully create an instance of Transation in the database
        """
        self.assertEqual(Transaction.objects.count(), 0)
        transaction = TransactionFactory.create()
        self.assertEqual(Transaction.objects.count(), 1)
        retrieved_transaction = Transaction.objects.first()

        self.assertEqual(transaction.company, retrieved_transaction.company)
        self.assertEqual(transaction.client, retrieved_transaction.client)
        self.assertEqual(transaction.value, retrieved_transaction.value)
        self.assertEqual(
            transaction.description, retrieved_transaction.description
        )

    def test_model_creation_invalid_client(self):
        """
        Should fail to create an instance of Transaction in the database
        when the client value is invalid
        """
        self.assertEqual(Transaction.objects.count(), 0)

        # tests invalid client (cpf) value
        transaction = TransactionFactory.build()
        transaction.company.save()
        transaction.client = "111.111.111-11"
        expected_messages = {
            "client": [
                f"Ensure the CPF is valid (it is {transaction.client})."
            ]
        }

        with self.assertRaises(ValidationError) as raised:
            transaction.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Transaction.objects.count(), 0)

        # tests invalid cpf length
        transaction = TransactionFactory.build()
        transaction.company.save()
        transaction.client = transaction.client + "1"
        expected_messages = {
            "client": [
                f"Ensure the CPF is valid (it is {transaction.client}).",
                f"Ensure this value has at most {CPF_SIZE} characters "
                f"(it has {len(transaction.client)}).",
            ],
        }

        with self.assertRaises(ValidationError) as raised:
            transaction.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_model_creation_empty_value(self):
        """
        Should fail to create an instance of Transaction in the database
        when the value is invalid
        """
        self.assertEqual(Transaction.objects.count(), 0)

        transaction = TransactionFactory.build()
        transaction.company.save()
        transaction.value = None
        expected_messages = {"value": ["This field cannot be null."]}

        with self.assertRaises(ValidationError) as raised:
            transaction.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_transaction_string_representation(self):
        transaction = TransactionFactory.build()
        self.assertEqual(
            str(transaction),
            f"Transaction (Value: {transaction.value} | "
            f"Company: {transaction.company.cnpj} | "
            f"Client: {transaction.client})",
        )
