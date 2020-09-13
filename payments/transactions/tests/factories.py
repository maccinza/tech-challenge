from companies.tests.factories import CompanyFactory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyAttribute, FuzzyFloat
from pycpfcnpj.gen import cpf_with_punctuation
from transactions.models import Transaction

MIN_VALUE = 150.00
MAX_VALUE = 5000.00


class TransactionFactory(DjangoModelFactory):
    company = SubFactory(CompanyFactory)
    client = FuzzyAttribute(cpf_with_punctuation)
    value = FuzzyFloat(MIN_VALUE, high=MAX_VALUE, precision=2)
    description = Faker("catch_phrase", locale="pt_BR")

    class Meta:
        model = Transaction
