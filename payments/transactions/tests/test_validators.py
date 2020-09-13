from django.core.validators import ValidationError
from django.test import TestCase

from pycpfcnpj.gen import cpf_with_punctuation
from transactions.validators import cpf_validator


class TestCpfValidator(TestCase):
    def test_cpf_validator(self):
        """Should successfully validate a valid CPF value"""
        cpf = cpf_with_punctuation()
        self.assertIsNone(cpf_validator(cpf))

    def test_cpf_validator_invalid(self):
        """
        Should fail to validate an invalid CPF value raising a
        ValidationError
        """
        cpf = "111.111.111-11"
        expected_messages = [f"Ensure the CPF is valid (it is {cpf})."]
        with self.assertRaises(ValidationError) as raised:
            cpf_validator(cpf)
        self.assertEqual(raised.exception.messages, expected_messages)
