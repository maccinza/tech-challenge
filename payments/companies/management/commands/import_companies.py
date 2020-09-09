import json
import os
from enum import Enum

from django.core.management.base import BaseCommand

from companies.utils import CompaniesData, import_companies


class MessageType(Enum):
    SUCCESS = "success"
    ERROR = "error"


class Command(BaseCommand):
    help = "Imports companies data from json file into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filepath", type=str, help="Path to the source json file"
        )

    def _write_message(
        self, message: str, message_type: MessageType = MessageType.SUCCESS,
    ):
        if message_type == MessageType.SUCCESS:
            self.stdout.write(self.style.SUCCESS(message))
        elif message_type == MessageType.ERROR:
            self.stdout.write(self.style.ERROR(message))

    def _collect_data(self, filepath: str) -> CompaniesData:
        data = []
        try:
            with open(filepath, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
        except Exception as exc:
            self._write_message(
                f"Error trying to read {filepath}. Got {str(exc)}",
                MessageType.ERROR,
            )

        return data

    def _perform_insertion(self, data: CompaniesData, filepath: str):
        error_msg = f"Error trying to import companies data from {filepath}."
        success_message = (
            f"Successfully imported companies data from {filepath}"
        )

        try:
            import_companies(data)
        except Exception as exc:
            self._write_message(
                f"{error_msg} Got {str(exc)}", MessageType.ERROR
            )
        else:
            self._write_message(success_message, MessageType.SUCCESS)

    def handle(self, *args, **options):
        filepath = options.get("filepath", "")

        path_exists = os.path.exists(filepath)
        is_file = os.path.isfile(filepath)
        is_json = filepath.endswith(".json")

        if path_exists and is_file and is_json:
            data = self._collect_data(filepath)

            if data:
                self._perform_insertion(data, filepath)
            else:
                self._write_message(
                    f"Could not collect data from {filepath} properly or the "
                    f"file is empty",
                    MessageType.ERROR,
                )
        else:
            self._write_message(
                f"Provided filepath {filepath} does not exist or is not a file",
                MessageType.ERROR,
            )
