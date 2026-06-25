from django.core.management.base import BaseCommand

from processing.models import (
    RetentionDataObject,
    RetentionRule,
    RetentionStorageSystem,
)


class Command(BaseCommand):
    help = "Seed-Daten für PROSSESSOR Retention Pilot 1A anlegen oder aktualisieren."

    def handle(self, *args, **options):
        data_objects = [
            {
                "name": "E-Mail Handelsbrief",
                "description": "Ein- oder ausgehende E-Mail mit Handelsbrief-/Geschäftsbriefcharakter.",
                "sort_order": 10,
            },
            {
                "name": "Rechnung",
                "description": "Rechnung oder rechnungsrelevanter Buchungsbeleg.",
                "sort_order": 20,
            },
            {
                "name": "Softwareeintrag",
                "description": "Strukturierter Eintrag in einer Fachsoftware, z. B. Mandats-/Kundendatensatz.",
                "sort_order": 30,
            },
        ]

        systems = [
            {
                "name": "Outlook / Exchange",
                "description": "E-Mail-System / Postfach / Exchange-Archiv.",
                "default_deletion_location": "Postfach-/Archivregel",
                "default_information_owner": "zuständige Fachabteilung / Postfachinhaber",
                "sort_order": 10,
            },
            {
                "name": "DATEV",
                "description": "Buchhaltungs-/Rechnungswesen-System.",
                "default_deletion_location": "Löschung/Archivierung nach Buchhaltungsroutine",
                "default_information_owner": "Buchhaltung / Steuerverantwortliche",
                "sort_order": 20,
            },
            {
                "name": "RA-MICRO",
                "description": "Kanzlei-/Mandatssoftware.",
                "default_deletion_location": "Löschung/Archivierung nach Kanzleisoftware-Routine",
                "default_information_owner": "Mandatsverantwortlicher / Kanzleileitung",
                "sort_order": 30,
            },
        ]

        for item in data_objects:
            RetentionDataObject.objects.update_or_create(
                name=item["name"],
                defaults=item,
            )

        for item in systems:
            RetentionStorageSystem.objects.update_or_create(
                name=item["name"],
                defaults=item,
            )

        email = RetentionDataObject.objects.get(name="E-Mail Handelsbrief")
        invoice = RetentionDataObject.objects.get(name="Rechnung")
        software_entry = RetentionDataObject.objects.get(name="Softwareeintrag")

        outlook = RetentionStorageSystem.objects.get(name="Outlook / Exchange")
        datev = RetentionStorageSystem.objects.get(name="DATEV")
        ra_micro = RetentionStorageSystem.objects.get(name="RA-MICRO")

        rules = [
            {
                "data_object": email,
                "storage_system": outlook,
                "retention_period_value": 6,
                "retention_period_unit": RetentionRule.PeriodUnit.YEARS,
                "trigger": "Schluss des Kalenderjahres der Entstehung bzw. des Vorgangs",
                "legal_basis": "HGB / AO, soweit Handels- oder Geschäftsbrief",
                "deletion_location": "Postfach-/Archivregel; Speicherort ist Outlook / Exchange",
                "information_owner_role": "Postfachinhaber / Fachabteilung",
                "requires_review": False,
                "note": "Pilotregel; fachlich im konkreten Verfahren prüfen.",
                "sort_order": 10,
            },
            {
                "data_object": invoice,
                "storage_system": datev,
                "retention_period_value": 10,
                "retention_period_unit": RetentionRule.PeriodUnit.YEARS,
                "trigger": "Schluss des Kalenderjahres der Buchung / des Belegs",
                "legal_basis": "AO / HGB",
                "deletion_location": "Buchhaltungsroutine; Speicherort ist DATEV",
                "information_owner_role": "Buchhaltung / Steuerverantwortliche",
                "requires_review": False,
                "note": "Pilotregel; konkrete gesetzliche Frist im Einzelfall prüfen.",
                "sort_order": 20,
            },
            {
                "data_object": software_entry,
                "storage_system": ra_micro,
                "retention_period_value": None,
                "retention_period_unit": RetentionRule.PeriodUnit.CHECK,
                "trigger": "Verfahrens-/Mandatsende oder Zweckfortfall",
                "legal_basis": "Einzelfallprüfung / berufsrechtliche Aufbewahrung",
                "deletion_location": "Kanzleisoftware-Routine; Speicherort ist RA-MICRO",
                "information_owner_role": "Mandatsverantwortlicher / Kanzleileitung",
                "requires_review": True,
                "note": "Pilotregel bewusst auf prüfen gesetzt.",
                "sort_order": 30,
            },
        ]

        for item in rules:
            RetentionRule.objects.update_or_create(
                data_object=item["data_object"],
                storage_system=item["storage_system"],
                defaults=item,
            )

        self.stdout.write(
            self.style.SUCCESS("Retention Pilot 1A Seed-Daten wurden angelegt/aktualisiert.")
        )
