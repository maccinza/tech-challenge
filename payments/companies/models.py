from uuid import uuid4

from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.functional import cached_property

from companies.validators import IntegerLengthValidator, cnpj_validator

CNPJ_SIZE = 18
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
        validators=[MinLengthValidator(CNPJ_SIZE), cnpj_validator],
        unique=True,
    )
    owner = models.CharField(max_length=OWNER_SIZE, blank=False, null=False)
    ddd = models.PositiveIntegerField(
        validators=[
            MinValueValidator(DDD_LOWER_LIMIT),
            MaxValueValidator(DDD_UPPER_LIMIT),
        ],
        blank=False,
        null=False,
    )
    phone = models.PositiveIntegerField(
        validators=[IntegerLengthValidator(PHONE_SIZE, PHONE_SIZE)]
    )

    @cached_property
    def full_phone(self):
        return int(f"{self.ddd}{self.phone}")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.cnpj})"
