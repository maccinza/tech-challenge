from django.core.validators import ValidationError
from django.test import TestCase

from companies.models import (
    CNPJ_SIZE,
    DDD_LOWER_LIMIT,
    DDD_UPPER_LIMIT,
    PHONE_SIZE,
    Company,
)
from companies.tests.factories import CompanyFactory


class TestCompanyModel(TestCase):
    def test_model_creation(self):
        """Should successfully create an instance of Company in the database"""
        self.assertEqual(Company.objects.count(), 0)
        company = CompanyFactory.create()
        self.assertEqual(Company.objects.count(), 1)
        retrieved_company = Company.objects.first()

        self.assertEqual(company.name, retrieved_company.name)
        self.assertEqual(company.cnpj, retrieved_company.cnpj)
        self.assertEqual(company.owner, retrieved_company.owner)
        self.assertEqual(company.ddd, retrieved_company.ddd)
        self.assertEqual(company.phone, retrieved_company.phone)

    def test_model_creation_duplicate_cnpj(self):
        """
        Should fail to create multiple instances of Company in the database
        with the same CNPJ
        """
        self.assertEqual(Company.objects.count(), 0)
        company = CompanyFactory.create()
        self.assertEqual(Company.objects.count(), 1)

        company_two = CompanyFactory.build()
        company_two.cnpj = company.cnpj

        expected_messages = {
            "cnpj": ["Company with this Cnpj already exists."]
        }
        with self.assertRaises(ValidationError) as raised:
            company_two.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)

    def test_model_creation_invalid_cnpj(self):
        """
        Should fail to create an instance of Company in the database when the
        cnpj value is invalid
        """
        self.assertEqual(Company.objects.count(), 0)

        # tests invalid cnpj value
        company = CompanyFactory.build()
        company.cnpj = "11.111.111/1111-11"
        expected_messages = {
            "cnpj": [f"Ensure the CNPJ is valid (it is {company.cnpj})."]
        }

        with self.assertRaises(ValidationError) as raised:
            company.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Company.objects.count(), 0)

        # tests invalid cnpj length
        company = CompanyFactory.build()
        company.cnpj = company.cnpj + "1"
        expected_messages = {
            "cnpj": [
                f"Ensure the CNPJ is valid (it is {company.cnpj}).",
                f"Ensure this value has at most {CNPJ_SIZE} characters "
                f"(it has {len(company.cnpj)}).",
            ],
        }

        with self.assertRaises(ValidationError) as raised:
            company.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Company.objects.count(), 0)

    def test_model_creation_invalid_ddd(self):
        """
        Should fail to create an instance of Company in the database when the
        ddd value is invalid
        """
        self.assertEqual(Company.objects.count(), 0)

        # tests invalid ddd value below lower limit
        company = CompanyFactory.build()
        company.ddd = 10
        expected_messages = {
            "ddd": [
                f"Ensure this value is greater than or equal to "
                f"{DDD_LOWER_LIMIT}."
            ]
        }

        with self.assertRaises(ValidationError) as raised:
            company.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Company.objects.count(), 0)

        # tests invalid ddd value above upper limit
        company = CompanyFactory.build()
        company.ddd = 100
        expected_messages = {
            "ddd": [
                f"Ensure this value is less than or equal to "
                f"{DDD_UPPER_LIMIT}."
            ]
        }

        with self.assertRaises(ValidationError) as raised:
            company.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Company.objects.count(), 0)

    def test_model_creation_invalid_phone(self):
        """
        Should fail to create an instance of Company in the database when the
        phone value is invalid
        """
        self.assertEqual(Company.objects.count(), 0)

        # tests invalid phone value below expected length
        company = CompanyFactory.build()
        company.phone = 11111111
        expected_messages = {
            "phone": [
                f"Ensure the length of this value is between {PHONE_SIZE} "
                f"and {PHONE_SIZE} (it is {len(str(company.phone))})."
            ]
        }

        with self.assertRaises(ValidationError) as raised:
            company.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Company.objects.count(), 0)

        # tests invalid phone value above expected length
        company = CompanyFactory.build()
        company.phone = 1111111111
        expected_messages = {
            "phone": [
                f"Ensure the length of this value is between {PHONE_SIZE} "
                f"and {PHONE_SIZE} (it is {len(str(company.phone))})."
            ]
        }

        with self.assertRaises(ValidationError) as raised:
            company.save()
        self.assertEqual(raised.exception.message_dict, expected_messages)
        self.assertEqual(Company.objects.count(), 0)

    def test_company_full_phone(self):
        """Should successfully get the full phone number of a Company"""
        company = CompanyFactory.build()
        self.assertEqual(
            company.full_phone, int(f"{company.ddd}{company.phone}")
        )

    def test_company_string_representation(self):
        """
        Should successfully get a correct string representation of a Company
        """
        company = CompanyFactory.build()
        self.assertEqual(str(company), f"{company.name} ({company.cnpj})")
