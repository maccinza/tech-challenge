from django.test import TestCase

from companies.api.serializers import CompanyReportSerializer
from companies.tests.factories import CompanyFactory

field_mappings = {
    "nome": "name",
    "cnpj": "cnpj",
    "dono": "owner",
    "telefone": "full_phone",
}


class TestCompanySerializers(TestCase):
    def test_company_report_serializer(self):
        company = CompanyFactory.build()
        serialized_data = CompanyReportSerializer(company).data

        for serializer_field, model_field in field_mappings.items():
            self.assertIn(serializer_field, serialized_data)
            value = getattr(company, model_field)

            if serializer_field == "telefone":
                value = str(value)

            self.assertEqual(serialized_data[serializer_field], value)
