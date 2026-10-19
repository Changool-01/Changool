from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

GROUP_NAMES = ("claim", "operation", "migration")


class Command(BaseCommand):
    help = "Create the claim, operation, and migration groups used by the project buttons."

    def handle(self, *args, **options):
        for name in GROUP_NAMES:
            _, created = Group.objects.get_or_create(name=name)
            state = "created" if created else "already present"
            self.stdout.write(f"{name}: {state}")
