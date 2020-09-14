from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.test import TestCase

from companies.api.serializers import CompanyReportSerializer
from companies.models import Company
from transactions.api.serializers import (
    ReportSerializer,
    TransactionReportSerializer,
    TransactionSerializer,
    WritableTransactionSerializer,
)
from transactions.models import Transaction
from transactions.tests.factories import TransactionFactory

transaction_report_fields_mapping = {
    "cliente": "client",
    "valor": "value",
    "descricao": "description",
}

transaction_reader_fields_mapping = {"estabelecimento": "company.cnpj"}
transaction_reader_fields_mapping.update(transaction_report_fields_mapping)

transaction_writer_fields_mapping = {"estabelecimento": "company"}
transaction_writer_fields_mapping.update(transaction_report_fields_mapping)


class TestSerializers(TestCase):
    def test_reader_serializer(self):
        """Should successfully serialize a Transaction instance"""
        transaction = TransactionFactory.build()
        serializer = TransactionSerializer(transaction)
        serialized_data = serializer.data

        for (
            serializer_field,
            model_field,
        ) in transaction_reader_fields_mapping.items():
            self.assertIn(serializer_field, serialized_data)

            if serializer_field == "estabelecimento":
                value = transaction.company.cnpj
            else:
                value = getattr(transaction, model_field)

            self.assertEqual(serialized_data[serializer_field], value)

        # tests if serializer validates
        serializer = TransactionSerializer(data=serialized_data)
        self.assertTrue(serializer.is_valid())

    def test_write_with_reader_serializer(self):
        """Should fail to write data with the Transaction reader serializer"""
        transaction = TransactionFactory.build()
        serialized_data = TransactionSerializer(transaction).data
        serializer = TransactionSerializer(data=serialized_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(Transaction.objects.count(), 0)
        expected_message = (
            "method does not support writable dotted-source fields by default"
        )
        with self.assertRaises(AssertionError) as raised:
            serializer.save()
        self.assertIn(expected_message, str(raised.exception))
        self.assertEqual(Transaction.objects.count(), 0)

    def test_writer_serializer(self):
        """Should successfully serialize a Transaction instance"""
        transaction = TransactionFactory.build()
        transaction.company.save()
        serializer = WritableTransactionSerializer(transaction)
        data = serializer.data

        for (
            serializer_field,
            model_field,
        ) in transaction_writer_fields_mapping.items():
            self.assertIn(serializer_field, data)
            value = getattr(transaction, model_field)

            if serializer_field == "estabelecimento":
                value = transaction.company.id

            self.assertEqual(data[serializer_field], value)

        # tests if serializer validates
        serializer = WritableTransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_writer_serializer_save(self):
        """
        Should successfully write data with the Transaction writer serializer
        when the Company for the given Transaction exists
        """
        transaction = TransactionFactory.build()
        transaction.company.save()
        self.assertEqual(Transaction.objects.count(), 0)

        data = WritableTransactionSerializer(transaction).data
        serializer = WritableTransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(Transaction.objects.count(), 1)

    def test_writer_serializer_no_company(self):
        """
        Should fail to validate data with the Transaction writer serializer
        when the Company for the given Transaction does not exist
        """
        transaction = TransactionFactory.build()
        self.assertEqual(Transaction.objects.count(), 0)

        data = WritableTransactionSerializer(transaction).data
        serializer = WritableTransactionSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        expected_key = "estabelecimento"
        expected_text = "object does not exist."
        self.assertIn(expected_key, serializer.errors)
        self.assertIn(expected_text, str(serializer.errors[expected_key]))
        self.assertEqual(Transaction.objects.count(), 0)

    def test_writer_serializer_save_invalid_client(self):
        """
        Should fail to save data with the Transaction writer serializer
        when the client cpf is invalid
        """
        transaction = TransactionFactory.build()
        transaction.company.save()
        transaction.client = "111.111.111-11"
        self.assertEqual(Transaction.objects.count(), 0)

        data = WritableTransactionSerializer(transaction).data
        serializer = WritableTransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        expected_messages = {
            "client": [
                f"Ensure the CPF is valid (it is {transaction.client})."
            ]
        }

        with self.assertRaises(ValidationError) as raised:
            serializer.save()

        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_transaction_report_serializer(self):
        """
        Should successfully serialize a Transaction instance when using
        the Transaction serializer for reports
        """
        transaction = TransactionFactory.build()
        serializer = TransactionReportSerializer(transaction)
        data = serializer.data

        for (
            serializer_field,
            model_field,
        ) in transaction_report_fields_mapping.items():
            self.assertIn(serializer_field, data)
            value = getattr(transaction, model_field)
            self.assertEqual(data[serializer_field], value)

        # tests if serializer validates
        serializer = TransactionReportSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_report_serializer(self):
        """
        Should successfully serialize a Company Transactions Report when using
        the Report serializer
        """
        transaction_one = TransactionFactory.build()
        transaction_one.company.save()
        transaction_one.save()
        company = transaction_one.company
        transaction_two = TransactionFactory.build()
        transaction_two.company = company
        transaction_two.save()

        # query for annotating the total value
        company = (
            Company.objects.filter(cnpj=company.cnpj)
            .prefetch_related("transactions")
            .annotate(total_value=Sum("transactions__value"))
            .first()
        )

        serializer = ReportSerializer(company)
        expected_data = {
            "estabelecimento": CompanyReportSerializer(company).data,
            "recebimentos": [
                TransactionReportSerializer(transaction_one).data,
                TransactionReportSerializer(transaction_two).data,
            ],
            "total_recebido": company.total_value,
        }

        self.assertEqual(serializer.data, expected_data)
