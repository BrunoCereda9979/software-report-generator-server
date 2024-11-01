from typing import Any
from django.core.management import BaseCommand
from django.core.management.base import CommandParser
import pandas as pd
from api.models import ContactPerson

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        xlsx_file = pd.read_excel('department_apps.xlsx', 'Contact People')
        print(xlsx_file)