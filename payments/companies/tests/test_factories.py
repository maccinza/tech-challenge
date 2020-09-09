from django.test import TestCase

from companies.models import (
    DDD_LOWER_LIMIT,
    DDD_UPPER_LIMIT,
    PHONE_SIZE,
    Company,
)
from companies.tests.factories import (
    COMPANY_TYPES,
    CompanyFactory,
    fake_company_name,
    fake_phone_number,
)


class TestFactories(TestCase):
    def test_fake_company(self):
        """
        Should successfully return a fake company name containing company type
        """
        company_name = fake_company_name()
        self.assertIsInstance(company_name, str)
        self.assertTrue(
            any([_type in company_name for _type in COMPANY_TYPES])
        )

    def test_fake_phone(self):
        """
        Should successfully return fake phone number with correct length
        """
        phone_number = fake_phone_number()
        self.assertIsInstance(phone_number, int)
        self.assertEqual(len(str(phone_number)), PHONE_SIZE)

    def test_company_factory(self):
        """
        Should successfully get an instance of Company with populated
        attributes
        """
        company = CompanyFactory()
        self.assertIsInstance(company, Company)
        self.assertIsInstance(company.name, str)
        self.assertTrue(len(company.name) > 1)
        self.assertIsInstance(company.cnpj, str)
        self.assertTrue(len(company.cnpj) > 1)
        self.assertIsInstance(company.owner, str)
        self.assertTrue(len(company.owner) > 1)
        self.assertIsInstance(company.ddd, int)
        self.assertGreaterEqual(company.ddd, DDD_LOWER_LIMIT)
        self.assertLessEqual(company.ddd, DDD_UPPER_LIMIT)
        self.assertIsInstance(company.phone, int)
        self.assertEqual(len(str(company.phone)), PHONE_SIZE)
