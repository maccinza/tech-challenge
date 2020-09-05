from random import choice

from companies.models import (
    DDD_LOWER_LIMIT,
    DDD_UPPER_LIMIT,
    PHONE_SIZE,
    Company,
)
from factory import Faker
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyAttribute, FuzzyInteger
from pycpfcnpj.gen import cnpj_with_punctuation

COMPANY_TYPES = ["LTDA", "Indústria e Comércio", "Consultoria", "Serviços"]


def fake_company_name() -> str:
    name = Faker("name", locale="pt_BR").generate()
    random_type = choice(COMPANY_TYPES)

    return f"{name} {choice(random_type)}"


def fake_phone_number() -> int:
    phone = Faker("msisdn", locale="pt_BR").generate()
    return int(phone[:PHONE_SIZE])


class CompanyFactory(DjangoModelFactory):
    name = FuzzyAttribute(fake_company_name)
    cnpj = FuzzyAttribute(cnpj_with_punctuation)
    owner = Faker("name", locale="pt_BR")
    ddd = FuzzyInteger(DDD_LOWER_LIMIT, DDD_UPPER_LIMIT)
    phone = FuzzyAttribute(fake_phone_number)

    class Meta:
        model = Company
