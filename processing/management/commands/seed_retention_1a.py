from django.core.management.base import BaseCommand

from processing.models import (
    RetentionDataObject,
    RetentionRule,
    RetentionStorageSystem,
)


class Command(BaseCommand):
    help = "Seed-Daten für PROSSESSOR Retention anlegen oder aktualisieren."

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
            {
                "name": "Dokument",
                "description": "Einzelnes Dokument oder Datei in einem Dokumenten- oder Dateisystem.",
                "sort_order": 40,
            },
            {
                "name": "Backup",
                "description": "Sicherungskopie, die regelmäßig überschrieben oder nach Backup-Routine gelöscht wird.",
                "sort_order": 90,
            },
        ]

        systems = [
            {
                "name": "E-Mail-System",
                "description": "Generisches E-Mail-System, wenn Outlook/Exchange oder ein anderer konkreter Anbieter nicht gesondert gepflegt wird.",
                "default_deletion_location": "Postfach-/Archivregel",
                "default_information_owner": "Postfachinhaber / zuständige Fachabteilung",
                "sort_order": 5,
            },
            {
                "name": "Outlook / Exchange",
                "description": "Konkretes E-Mail-System / Postfach / Exchange-Archiv.",
                "default_deletion_location": "Postfach-/Archivregel",
                "default_information_owner": "zuständige Fachabteilung / Postfachinhaber",
                "sort_order": 10,
            },
            {
                "name": "Anwaltssoftware",
                "description": "Generische Kanzlei-/Mandatssoftware, wenn RA-MICRO, Advoware, AnNoText usw. nicht einzeln gepflegt werden.",
                "default_deletion_location": "Kanzleisoftware-Routine",
                "default_information_owner": "Mandatsverantwortlicher / Kanzleileitung",
                "sort_order": 15,
            },
            {
                "name": "RA-MICRO",
                "description": "Konkrete Kanzlei-/Mandatssoftware.",
                "default_deletion_location": "RA-MICRO / Kanzleisoftware-Routine",
                "default_information_owner": "Mandatsverantwortlicher / Kanzleileitung",
                "sort_order": 20,
            },
            {
                "name": "Praxissoftware",
                "description": "Generische Arzt-/Praxissoftware, wenn das konkrete System nicht einzeln gepflegt wird.",
                "default_deletion_location": "Praxissoftware-Routine",
                "default_information_owner": "Praxisleitung / behandelnde Stelle",
                "sort_order": 25,
            },
            {
                "name": "CRM",
                "description": "Generisches Customer-Relationship-Management-System.",
                "default_deletion_location": "CRM-Löschroutine",
                "default_information_owner": "Vertrieb / Kundenmanagement",
                "sort_order": 30,
            },
            {
                "name": "ERP",
                "description": "Generisches Enterprise-Resource-Planning-System.",
                "default_deletion_location": "ERP-Löschroutine",
                "default_information_owner": "Verwaltung / Fachabteilung",
                "sort_order": 35,
            },
            {
                "name": "DATEV",
                "description": "Buchhaltungs-/Rechnungswesen-System.",
                "default_deletion_location": "Löschung/Archivierung nach Buchhaltungsroutine",
                "default_information_owner": "Buchhaltung / Steuerverantwortliche",
                "sort_order": 40,
            },
            {
                "name": "DMS",
                "description": "Generisches Dokumentenmanagementsystem.",
                "default_deletion_location": "DMS-Löschroutine",
                "default_information_owner": "Dokumentenverantwortlicher / Fachabteilung",
                "sort_order": 50,
            },
            {
                "name": "Fileserver",
                "description": "Dateiablage, Netzlaufwerk oder lokaler Server.",
                "default_deletion_location": "Dateiablage / Ordnerstruktur",
                "default_information_owner": "Fachabteilung / IT",
                "sort_order": 60,
            },
            {
                "name": "Backup-System",
                "description": "Generisches Backup-System mit Löschung über Backup-Rotation.",
                "default_deletion_location": "Backup-Rotation",
                "default_information_owner": "IT / Systemadministration",
                "sort_order": 90,
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

        def obj(name):
            return RetentionDataObject.objects.get(name=name)

        def sys(name):
            return RetentionStorageSystem.objects.get(name=name)

        rules = [
            {
                "data_object": obj("E-Mail Handelsbrief"),
                "storage_system": sys("E-Mail-System"),
                "retention_period_value": 6,
                "retention_period_unit": RetentionRule.PeriodUnit.YEARS,
                "trigger": "Schluss des Kalenderjahres der Entstehung bzw. des Vorgangs",
                "legal_basis": "HGB / AO, soweit Handels- oder Geschäftsbrief",
                "deletion_location": "Postfach-/Archivregel",
                "information_owner_role": "Postfachinhaber / Fachabteilung",
                "requires_review": False,
                "note": "Generische Regel für E-Mail-Systeme.",
                "sort_order": 10,
            },
            {
                "data_object": obj("E-Mail Handelsbrief"),
                "storage_system": sys("Outlook / Exchange"),
                "retention_period_value": 6,
                "retention_period_unit": RetentionRule.PeriodUnit.YEARS,
                "trigger": "Schluss des Kalenderjahres der Entstehung bzw. des Vorgangs",
                "legal_basis": "HGB / AO, soweit Handels- oder Geschäftsbrief",
                "deletion_location": "Postfach-/Archivregel; Speicherort ist Outlook / Exchange",
                "information_owner_role": "Postfachinhaber / Fachabteilung",
                "requires_review": False,
                "note": "Konkrete Regel für Outlook / Exchange.",
                "sort_order": 11,
            },
            {
                "data_object": obj("Rechnung"),
                "storage_system": sys("DATEV"),
                "retention_period_value": 10,
                "retention_period_unit": RetentionRule.PeriodUnit.YEARS,
                "trigger": "Schluss des Kalenderjahres der Buchung / des Belegs",
                "legal_basis": "AO / HGB",
                "deletion_location": "Buchhaltungsroutine; Speicherort ist DATEV",
                "information_owner_role": "Buchhaltung / Steuerverantwortliche",
                "requires_review": False,
                "note": "Konkrete Regel für DATEV.",
                "sort_order": 20,
            },
            {
                "data_object": obj("Softwareeintrag"),
                "storage_system": sys("Anwaltssoftware"),
                "retention_period_value": None,
                "retention_period_unit": RetentionRule.PeriodUnit.CHECK,
                "trigger": "Verfahrens-/Mandatsende oder Zweckfortfall",
                "legal_basis": "Einzelfallprüfung / berufsrechtliche Aufbewahrung",
                "deletion_location": "Kanzleisoftware-Routine",
                "information_owner_role": "Mandatsverantwortlicher / Kanzleileitung",
                "requires_review": True,
                "note": "Generische Regel für Kanzlei-/Mandatssoftware.",
                "sort_order": 30,
            },
            {
                "data_object": obj("Softwareeintrag"),
                "storage_system": sys("RA-MICRO"),
                "retention_period_value": None,
                "retention_period_unit": RetentionRule.PeriodUnit.CHECK,
                "trigger": "Verfahrens-/Mandatsende oder Zweckfortfall",
                "legal_basis": "Einzelfallprüfung / berufsrechtliche Aufbewahrung",
                "deletion_location": "RA-MICRO / Kanzleisoftware-Routine",
                "information_owner_role": "Mandatsverantwortlicher / Kanzleileitung",
                "requires_review": True,
                "note": "Konkrete Regel für RA-MICRO.",
                "sort_order": 31,
            },
            {
                "data_object": obj("Backup"),
                "storage_system": sys("Backup-System"),
                "retention_period_value": None,
                "retention_period_unit": RetentionRule.PeriodUnit.CHECK,
                "trigger": "Backup-Rotation / technisches Löschkonzept",
                "legal_basis": "Technisch-organisatorische Löschroutine; Einzelfallprüfung",
                "deletion_location": "Backup-Rotation",
                "information_owner_role": "IT / Systemadministration",
                "requires_review": True,
                "note": "Backups werden regelmäßig nicht einzeln gelöscht, sondern über Rotation und Wiederherstellungskonzepte gesteuert.",
                "sort_order": 90,
            },
        ]

        for item in rules:
            RetentionRule.objects.update_or_create(
                data_object=item["data_object"],
                storage_system=item["storage_system"],
                defaults=item,
            )

        self.stdout.write(
            self.style.SUCCESS("Retention Phase 2.2 Seed-Daten wurden angelegt/aktualisiert.")
        )
