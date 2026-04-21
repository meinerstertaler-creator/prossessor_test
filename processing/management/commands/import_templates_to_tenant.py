from django.core.management.base import BaseCommand, CommandError

from accounts.models import Tenant
from processing.models import Department, ProcessingActivity, ProcessingTemplate


class Command(BaseCommand):
    help = "Importiert Standardverfahren für einen bestimmten Mandanten"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant",
            type=str,
            required=True,
            help="Name des Mandanten, für den importiert werden soll",
        )
        parser.add_argument(
            "--group",
            type=str,
            default="general",
            help="Vorlagengruppe: general, medical, legal oder all",
        )

    def handle(self, *args, **options):
        tenant_name = options["tenant"]
        group = options["group"]

        try:
            tenant = Tenant.objects.get(name=tenant_name)
        except Tenant.DoesNotExist:
            raise CommandError(f"Mandant '{tenant_name}' wurde nicht gefunden.")

        templates = ProcessingTemplate.objects.filter(is_active=True)

        if group != "all":
            templates = templates.filter(template_group=group)

        templates = templates.order_by("title")

        if not templates.exists():
            raise CommandError(f"Keine aktiven Vorlagen für Gruppe '{group}' gefunden.")

        created_departments = 0
        created_processing = 0
        counter = 1

        for template in templates:
            department_obj = None

            if template.department:
                department_obj, dept_created = Department.objects.get_or_create(
                    tenant=tenant,
                    name=template.department,
                )
                if dept_created:
                    created_departments += 1

            internal_id = f"V{counter:03d}"
            while ProcessingActivity.objects.filter(
                tenant=tenant,
                internal_id=internal_id
            ).exists():
                counter += 1
                internal_id = f"V{counter:03d}"

            _, created = ProcessingActivity.objects.get_or_create(
                tenant=tenant,
                title=template.title,
                defaults={
                    "internal_id": internal_id,
                    "department": department_obj,
                    "purpose": template.purpose or "",
                    "description": template.description or template.purpose or "",
                    "status": ProcessingActivity.Status.ACTIVE,
                    "data_subject_categories": template.data_subject_categories or "",
                    "personal_data_categories": template.personal_data_categories or "",
                    "recipients": template.recipients or "",
                    "retention_period": template.retention_period or "",
                    "tom_summary": template.tom_summary or "",
                },
            )

            if created:
                created_processing += 1
                counter += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import abgeschlossen. Gruppe: {group}. "
                f"Neue Fachbereiche: {created_departments}, "
                f"neue Verarbeitungsvorgänge: {created_processing}"
            )
        )