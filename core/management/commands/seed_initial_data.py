from django.core.management.base import BaseCommand
from accounts.models import Role
from audits.models import AuditQuestion


class Command(BaseCommand):
    help = 'Legt initiale Rollen und Auditfragen an.'

    def handle(self, *args, **options):
        roles = [
            'Admin',
            'Datenschutzbeauftragter',
            'Bearbeiter',
            'Leser',
        ]
        for name in roles:
            Role.objects.get_or_create(name=name)

        questions = [
            ('contractual', 'Ist ein aktueller AV-Vertrag vorhanden?', 10),
            ('tom', 'Liegt eine aktuelle TOM-Dokumentation vor?', 20),
            ('subprocessors', 'Sind Unterauftragsverarbeiter dokumentiert?', 30),
            ('privacy_organisation', 'Ist ein Verfahren für Datenschutzvorfälle beschrieben?', 40),
            ('third_country', 'Sind Drittlandtransfers dokumentiert?', 50),
            ('evidence', 'Liegen aktuelle Zertifikate oder Nachweise vor?', 60),
        ]
        for category, question_text, sort_order in questions:
            AuditQuestion.objects.get_or_create(
                category=category,
                question_text=question_text,
                defaults={'sort_order': sort_order, 'is_active': True},
            )

        self.stdout.write(self.style.SUCCESS('Initialdaten wurden angelegt oder waren bereits vorhanden.'))
