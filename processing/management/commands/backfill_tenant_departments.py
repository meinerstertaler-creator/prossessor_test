from django.core.management.base import BaseCommand

from accounts.models import Tenant
from processing.models import Department
from processing.signals import ensure_default_departments_for_tenant


class Command(BaseCommand):
    help = "Legt fehlende Standard-Fachbereiche für bestehende Tenants an."

    def handle(self, *args, **options):
        self.stdout.write("Prüfe bestehende Tenants ...")

        tenants = Tenant.objects.all().order_by("name")
        total_created = 0

        for tenant in tenants:
            before_count = Department.objects.filter(tenant=tenant).count()

            ensure_default_departments_for_tenant(tenant)

            after_count = Department.objects.filter(tenant=tenant).count()
            created_count = max(after_count - before_count, 0)
            total_created += created_count

            self.stdout.write(
                f"- {tenant.name}: {created_count} Fachbereich(e) ergänzt"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Fertig. Insgesamt {total_created} Fachbereich(e) angelegt."
            )
        )