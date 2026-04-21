from django.core.management.base import BaseCommand

from actions.models import ActionItem
from dpia.models import DPIA, DPIACheck, DPIAMeasure, DPIARisk
from legal.models import LegalAssessment
from processing.models import ProcessingActivity


class Command(BaseCommand):
    help = "Löscht alle Falldaten, behält aber Stammdaten wie Standardfälle, Fachbereiche, Benutzer und Mandanten."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Bestätigung überspringen und Reset direkt ausführen.",
        )

    def handle(self, *args, **options):
        confirmed = options["yes"]

        if not confirmed:
            self.stdout.write(self.style.WARNING("Es werden alle Falldaten gelöscht:"))
            self.stdout.write("- Verfahren")
            self.stdout.write("- Rechtsbewertungen")
            self.stdout.write("- DSFA, Risiken und DSFA-Maßnahmen")
            self.stdout.write("- Maßnahmen")
            self.stdout.write("")
            self.stdout.write("Stammdaten bleiben erhalten:")
            self.stdout.write("- Standardfälle")
            self.stdout.write("- Fachbereiche")
            self.stdout.write("- Benutzer / Rollen / Mandanten")
            self.stdout.write("")

            answer = input("Wirklich fortfahren? Tippe 'JA': ").strip()
            if answer != "JA":
                self.stdout.write(self.style.ERROR("Abgebrochen."))
                return

        dpia_risks_deleted, _ = DPIARisk.objects.all().delete()
        dpia_measures_deleted, _ = DPIAMeasure.objects.all().delete()
        dpias_deleted, _ = DPIA.objects.all().delete()
        dpia_checks_deleted, _ = DPIACheck.objects.all().delete()
        legal_deleted, _ = LegalAssessment.objects.all().delete()
        actions_deleted, _ = ActionItem.objects.all().delete()
        processing_deleted, _ = ProcessingActivity.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Falldaten wurden gelöscht."))
        self.stdout.write(f"Verfahren gelöscht: {processing_deleted}")
        self.stdout.write(f"Rechtsbewertungen gelöscht: {legal_deleted}")
        self.stdout.write(f"DSFA-Prüfungen gelöscht: {dpia_checks_deleted}")
        self.stdout.write(f"DSFA gelöscht: {dpias_deleted}")
        self.stdout.write(f"DSFA-Risiken gelöscht: {dpia_risks_deleted}")
        self.stdout.write(f"DSFA-Maßnahmen gelöscht: {dpia_measures_deleted}")
        self.stdout.write(f"Maßnahmen gelöscht: {actions_deleted}")