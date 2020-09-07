from django.core.validators import ValidationError
from django.test import TestCase

from companies.validators import IntegerLengthValidator, cnpj_validator
from pycpfcnpj.gen import cnpj_with_punctuation


class TestCnpjValidator(TestCase):
    def test_cnpj_validator(self):
        """Should successfully validate a valid CNPJ value"""
        cnpj = cnpj_with_punctuation()
        self.assertIsNone(cnpj_validator(cnpj))

    def test_cnpj_validator_invalid(self):
        """
        Should fail to validate an invalid CNPJ value raising a
        ValidationError
        """
        cnpj = "111111111111111111"
        expected_messages = [f"Ensure the CNPJ is valid (it is {cnpj})."]
        with self.assertRaises(ValidationError) as raised:
            cnpj_validator(cnpj)
        self.assertEqual(raised.exception.messages, expected_messages)


class TestIntegerLengthValidator(TestCase):
    def test_instances_comparison(self):
        """
        Should be able to compare IntegerLengthValidator instances for
        equality/inequality
        """
        # tests for equality
        first_instance = IntegerLengthValidator(1, 3)
        second_instance = IntegerLengthValidator(1, 3)
        self.assertEqual(first_instance, second_instance)

        # tests for inequality
        second_instance = IntegerLengthValidator(1, 4)
        self.assertNotEqual(first_instance, second_instance)

    def test_integer_length_validation(self):
        """Should validate an integer whose length is within valid limits"""
        validator = IntegerLengthValidator(1, 2)
        self.assertIsNone(validator(5))
        self.assertIsNone(validator(27))
        self.assertIsNone(validator(99))

    def test_integer_length_validation_fail(self):
        """
        Should failt to validate an integer whose length is not within valid
        limits raising ValidationError
        """
        lower_limit = 1
        upper_limit = 2
        invalid_value = 325
        expected_messages = [
            f"Ensure the length of this value is between {lower_limit} and "
            f"{upper_limit} (it is {len(str(invalid_value))})."
        ]

        validator = IntegerLengthValidator(lower_limit, upper_limit)
        with self.assertRaises(ValidationError) as raised:
            self.assertIsNone(validator(invalid_value))
        self.assertEqual(raised.exception.messages, expected_messages)
