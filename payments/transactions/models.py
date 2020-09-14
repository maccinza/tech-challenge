from uuid import uuid4

from django.core.validators import MinLengthValidator
from django.db import models

from transactions.validators import cpf_validator

CPF_SIZE = 14
DESCRIPTION_LENGTH = 1000


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        related_name="transactions",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )
    client = models.CharField(
        max_length=CPF_SIZE,
        null=False,
        blank=False,
        validators=[MinLengthValidator(CPF_SIZE), cpf_validator],
    )
    value = models.FloatField(null=False, blank=False)
    description = models.TextField(
        max_length=DESCRIPTION_LENGTH, null=False, blank=False
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Transaction (Value: {self.value} | "
            f"Company: {self.company.cnpj} | Client: {self.client})"
        )
