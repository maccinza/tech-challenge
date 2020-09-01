from typing import Dict, List, Union

from .models import Company

CompanyData = Dict[str, Union[str, int]]
CompaniesData = List[CompanyData]


def import_companies(data: CompaniesData):
    """Imports companies data into the database"""
    companies_to_insert = []

    for piece in data:
        company = Company(**piece)
        companies_to_insert.append(company)

    Company.objects.bulk_create(companies_to_insert, ignore_conflicts=True)
