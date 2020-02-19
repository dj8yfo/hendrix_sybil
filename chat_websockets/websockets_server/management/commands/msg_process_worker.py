from django.core.management import BaseCommand
import importlib

from websockets_server.core import settings


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, default=settings.REDIS_HOST)
        parser.add_argument('--port', type=str, default=settings.REDIS_PORT)
        parser.add_argument('--sub_topic', type=str, required=True)
        parser.add_argument('--worker_class', type=str, required=True)

    def handle(self, *args, **options):
        module_name, class_name = options['worker_class'].split(':')
        mod = importlib.import_module(module_name)
        class_ = getattr(mod, class_name)
        class_(**options).run()
