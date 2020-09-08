from typing import Dict

from django.test import TransactionTestCase

from companies.models import Company
from companies.tests.factories import CompanyFactory
from companies.utils import import_companies


def remove_attributes(data: Dict) -> Dict:
    attributes_to_remove = {"_state", "id"}
    for attribute in attributes_to_remove:
        del data[attribute]
    return data


class TestUtils(TransactionTestCase):
    def setUp(self):
        self.test_data = {}
        companies = [
            CompanyFactory.build().__dict__,
            CompanyFactory.build().__dict__,
        ]
        for data in companies:
            clean_data = remove_attributes(data)
            self.test_data[clean_data["cnpj"]] = clean_data

    def test_import_companies(self):
        """
        Should successfully import distinct Companies data into the database
        """
        self.assertEqual(Company.objects.count(), 0)

        with self.assertNumQueries(1):
            import_companies(self.test_data.values())

        self.assertEqual(Company.objects.count(), len(self.test_data))

        for cnpj, data in self.test_data.items():
            company = Company.objects.get(cnpj=cnpj)
            company_dict = remove_attributes(company.__dict__)
            self.assertEqual(company_dict, data)

    def test_import_companies_ignoring_duplicates(self):
        """
        Should successfully import Company data into the database ignoring
        duplicates
        """
        self.assertEqual(Company.objects.count(), 0)

        first_key = list(self.test_data.keys())[0]
        test_element = self.test_data[first_key]
        test_data = [test_element, test_element]

        with self.assertNumQueries(1):
            import_companies(test_data)

        self.assertEqual(Company.objects.count(), 1)

        company = Company.objects.get(cnpj=test_element["cnpj"])
        company_dict = remove_attributes(company.__dict__)
        self.assertEqual(company_dict, test_element)
