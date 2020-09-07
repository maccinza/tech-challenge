from django.core.validators import BaseValidator, ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from pycpfcnpj.cpfcnpj import validate as cnpj_is_valid


def cnpj_validator(value: str):
    message = f"Ensure the CNPJ is valid (it is {value})."
    code = "cnpj_value"
    params = {"value": value}

    if not cnpj_is_valid(value):
        raise ValidationError(message, code=code, params=params)


@deconstructible
class IntegerLengthValidator(BaseValidator):
    message = _(
        "Ensure the length of this value is between %(lower_limit)s "
        "and %(upper_limit)s (it is %(show_value)s)."
    )
    code = "integer_length"

    def __init__(self, lower_limit, upper_limit, message=None):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        if message:
            self.message = message

    def __call__(self, value):
        cleaned = self.clean(value)
        lower_limit = self.lower_limit
        upper_limit = self.upper_limit

        params = {
            "lower_limit": lower_limit,
            "upper_limit": upper_limit,
            "show_value": len(str(cleaned)),
            "value": value,
        }
        if self.compare(cleaned, lower_limit, upper_limit):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            self.lower_limit == other.lower_limit
            and self.upper_limit == other.upper_limit
            and self.message == other.message
            and self.code == other.code
        )

    def compare(self, value, lower_limit, upper_limit):
        length = len(str(value))
        return length < lower_limit or length > upper_limit
