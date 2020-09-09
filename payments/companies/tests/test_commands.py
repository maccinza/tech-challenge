import json
import os
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from companies.management.commands.import_companies import Command, MessageType
from companies.models import Company

DATA_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    ),
    "data",
)
DATA_FILE = os.path.join(DATA_DIR, "companies.json")


class TestImportCompaniesCommand(TestCase):
    def test_write_message(self):
        """Command messages are correctly written to stdout"""
        output = StringIO()
        command = Command()
        success_message = f"This is a {MessageType.SUCCESS.value} test message"
        error_message = f"This is an {MessageType.ERROR.value} test message"

        with patch.object(command, "stdout", new=output):
            command._write_message(success_message, MessageType.SUCCESS)
            command._write_message(error_message, MessageType.ERROR)

        self.assertIn(success_message, output.getvalue())
        self.assertIn(error_message, output.getvalue())

    def test_successful_collect_data(self):
        """
        Should be able to read the input file data into list
        """
        command = Command()
        data = command._collect_data(DATA_FILE)
        self.assertIsInstance(data, list)
        with open(DATA_FILE, "r") as json_file:
            self.assertEqual(data, json.load(json_file))

    def test_failing_collect_data(self):
        """
        Should properly write to stdout when failing to collect data from file
        """
        output = StringIO()
        command = Command()

        error_message = "Simulated error message"
        expected_message = (
            f"Error trying to read {DATA_FILE}. Got {error_message}"
        )

        with patch.object(command, "stdout", new=output):
            with patch("builtins.open", side_effect=IOError(error_message)):
                command._collect_data(DATA_FILE)

        self.assertIn(expected_message, output.getvalue())

    def test_successful_perform_insertion(self):
        """Should properly insert provided companies data into the database"""
        output = StringIO()
        command = Command()
        data = command._collect_data(DATA_FILE)

        self.assertEqual(Company.objects.count(), 0)
        with patch.object(command, "stdout", new=output):
            command._perform_insertion(data, DATA_FILE)

        self.assertEqual(Company.objects.count(), len(data))
        self.assertIn(
            f"Successfully imported companies data from {DATA_FILE}",
            output.getvalue(),
        )

        companies = Company.objects.all()
        cnpjs = [piece["cnpj"] for piece in data]
        for company in companies:
            self.assertIn(company.cnpj, cnpjs)

    def test_perform_insertion_failure(self):
        """
        Should properly write to stdout when failing to import companies data
        """
        output = StringIO()
        command = Command()
        error_message = "Simulated error message"

        data = command._collect_data(DATA_FILE)

        self.assertEqual(Company.objects.count(), 0)
        with patch.object(command, "stdout", new=output):
            with patch(
                "companies.management.commands.import_companies."
                "import_companies",
                side_effect=IOError(error_message),
            ):
                command._perform_insertion(data, DATA_FILE)

        self.assertIn(
            f"Error trying to import companies data from {DATA_FILE}",
            output.getvalue(),
        )
        self.assertIn(error_message, output.getvalue())
        self.assertEqual(Company.objects.count(), 0)

    def test_successful_command(self):
        """
        Should successfully insert the companies data into the database when
        running the command
        """
        output = StringIO()
        self.assertEqual(Company.objects.count(), 0)

        kwarguments = {"filepath": DATA_FILE, "stdout": output}
        call_command("import_companies", **kwarguments)

        with open(DATA_FILE, "r") as json_file:
            expected_data = json.load(json_file)

        self.assertEqual(Company.objects.count(), len(expected_data))
        self.assertIn(
            f"Successfully imported companies data from {DATA_FILE}",
            output.getvalue(),
        )

    def test_failing_command_data(self):
        """
        Should properly write to stdout when failing to collect the data
        when running the command
        """
        output = StringIO()
        self.assertEqual(Company.objects.count(), 0)

        kwarguments = {"filepath": DATA_FILE, "stdout": output}

        with patch(
            "companies.management.commands.import_companies.Command._collect_data",
            return_value=None,
        ):
            call_command("import_companies", **kwarguments)

        self.assertEqual(Company.objects.count(), 0)
        self.assertIn(
            f"Could not collect data from {DATA_FILE} properly or the "
            f"file is empty",
            output.getvalue(),
        )

    def test_failing_command_file(self):
        """
        Should properly write to stdout when failing to access the data file
        when running the command
        """
        output = StringIO()
        self.assertEqual(Company.objects.count(), 0)

        kwarguments = {"filepath": DATA_FILE, "stdout": output}

        with patch("os.path.exists", return_value=False):
            call_command("import_companies", **kwarguments)

        self.assertEqual(Company.objects.count(), 0)
        self.assertIn(
            f"Provided filepath {DATA_FILE} does not exist or is not a file",
            output.getvalue(),
        )
