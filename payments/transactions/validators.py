from django.core.validators import ValidationError

from pycpfcnpj.cpfcnpj import validate as cpf_is_valid


def cpf_validator(value: str):
    message = f"Ensure the CPF is valid (it is {value})."
    code = "cpf_value"
    params = {"value": value}

    if not cpf_is_valid(value):
        raise ValidationError(message, code=code, params=params)
