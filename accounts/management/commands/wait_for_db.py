import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('データベースの準備を待っています...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('データベースが利用できません。1秒待機します...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('データベースが利用可能になりました！'))