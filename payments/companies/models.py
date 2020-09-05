from uuid import uuid4

from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.functional import cached_property

from pycpfcnpj.cpfcnpj import validate as CNPJValidator

CNPJ_SIZE = 18
DDD_SIZE = 2
DDD_LOWER_LIMIT = 11
DDD_UPPER_LIMIT = 99
NAME_SIZE = 255
OWNER_SIZE = 40
PHONE_SIZE = 9


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=NAME_SIZE, blank=False, null=False)
    cnpj = models.CharField(
        max_length=CNPJ_SIZE,
        blank=False,
        null=False,
        validators=[MinLengthValidator(CNPJ_SIZE), CNPJValidator],
        unique=True,
    )
    owner = models.CharField(max_length=OWNER_SIZE, blank=False, null=False)
    ddd = models.PositiveIntegerField(
        validators=[
            MinLengthValidator(DDD_SIZE),
            MaxLengthValidator(DDD_SIZE),
            MinValueValidator(DDD_LOWER_LIMIT),
            MaxValueValidator(DDD_UPPER_LIMIT),
        ],
        blank=False,
        null=False,
    )
    phone = models.PositiveIntegerField(
        validators=[
            MinLengthValidator(PHONE_SIZE),
            MaxLengthValidator(PHONE_SIZE),
        ]
    )

    @cached_property
    def full_phone(self):
        return f"{self.ddd}{self.phone}"

    def __str__(self):
        return f"{self.name} ({self.cnpj})"
