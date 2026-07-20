from django.core.management.base import BaseCommand

from processing.models import RetentionStorageLocation, RetentionStorageSystem


class Command(BaseCommand):
    help = "Konkrete Löschorte / Systeme für generische Löschort-Typen anlegen oder aktualisieren."

    def handle(self, *args, **options):
        locations_by_type = {
            "E-Mail-System": [("Outlook / Exchange", True), ("Microsoft 365 / Exchange Online", True), ("Gmail / Google Workspace", False), ("Thunderbird / IMAP-Postfach", False)],
            "Anwaltssoftware": [("RA-MICRO", True), ("Advoware", False), ("AnNoText", False), ("DATEV Anwalt", False), ("Legalvisio", False)],
            "Praxissoftware": [("MEDISTAR", False), ("TURBOMED", False), ("CGM ALBIS", False), ("x.concept", False), ("Doctolib", False)],
            "CRM": [("Salesforce", False), ("HubSpot", False), ("Microsoft Dynamics CRM", False), ("Pipedrive", False)],
            "ERP": [("SAP", False), ("Microsoft Dynamics 365", False), ("Oracle NetSuite", False), ("Sage", False), ("Lexware", False)],
            "DMS": [("ELO", False), ("DocuWare", False), ("SharePoint", True), ("d.velop", False), ("OpenText", False)],
            "Fileserver": [("Windows Fileserver", True), ("NAS", False), ("SharePoint Dokumentbibliothek", False)],
            "Messenger": [("Microsoft Teams", False), ("Slack", False), ("WhatsApp Business", False), ("Signal", False)],
            "Papierakte": [("Papierakte", False), ("Archivraum", False), ("Kellerarchiv", False), ("Aktenschrank", False)],
            "Backup-System": [("Veeam", False), ("Acronis", False), ("Windows Server Backup", False), ("Cloud Backup", False)],
        }

        for type_name, locations in locations_by_type.items():
            storage_system, _ = RetentionStorageSystem.objects.get_or_create(
                name=type_name,
                defaults={
                    "description": f"Generischer Löschort-Typ: {type_name}.",
                    "sort_order": 100,
                    "is_active": True,
                },
            )

            for index, (location_name, is_default) in enumerate(locations, start=1):
                RetentionStorageLocation.objects.update_or_create(
                    storage_system=storage_system,
                    name=location_name,
                    defaults={
                        "description": f"Konkreter Löschort / konkretes System zu {type_name}.",
                        "is_default": is_default,
                        "is_active": True,
                        "sort_order": index * 10,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Löschorte / Systeme wurden angelegt/aktualisiert."))
