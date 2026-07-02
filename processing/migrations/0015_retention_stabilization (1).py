# Generated for PROSSESSOR Retention Stabilization
# Aligns migration state after 0014 with the stabilized Retention models.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("processing", "0014_retentiondataobject_retentionstoragesystem_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="retentionstoragesystem",
            options={
                "ordering": ["sort_order", "name"],
                "verbose_name": "Speicherort / System",
                "verbose_name_plural": "Speicherorte / Systeme",
            },
        ),
        migrations.RemoveField(model_name="retentiondataobject", name="technical_key"),
        migrations.RemoveField(model_name="retentionstoragesystem", name="technical_key"),
        migrations.RemoveField(model_name="retentionrule", name="technical_key"),
        migrations.RemoveField(model_name="retentionrule", name="rule_type"),
        migrations.RemoveField(model_name="retentionrule", name="is_na_rule"),
        migrations.RemoveField(model_name="retentionrule", name="source_note"),
        migrations.AlterField(
            model_name="retentionstoragesystem",
            name="default_deletion_location",
            field=models.CharField(
                "Standard-Umsetzungshinweis",
                blank=True,
                help_text="Optionaler Standardhinweis zur praktischen Löschroutine in diesem System, z. B. Postfachregel, Archivroutine, Backup-Rotation.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="retentionrule",
            name="deletion_location",
            field=models.CharField(
                "Umsetzungshinweis / Löschroutine",
                blank=True,
                help_text="Optionaler Hinweis zur praktischen Umsetzung, z. B. Postfachregel, Archivroutine, Backup-Rotation. Der eigentliche Speicherort ist das ausgewählte System.",
                max_length=255,
            ),
        ),
        migrations.CreateModel(
            name="ProcessingRetentionAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("complete", "Vollständig"), ("check", "Prüfen"), ("incomplete", "Unvollständig"), ("not_applicable", "Nicht einschlägig")], default="incomplete", max_length=30)),
                ("custom_note", models.TextField(blank=True, help_text="Hinweis oder Abweichung im konkreten Verfahren.")),
                ("na_reason", models.TextField(blank=True, help_text="Begründung, wenn kein Löschkonzept erforderlich ist.")),
                ("sort_order", models.PositiveIntegerField(default=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("applied_rule", models.ForeignKey(blank=True, help_text="Automatisch passende oder manuell gewählte Löschregel.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="processing_assignments", to="processing.retentionrule")),
                ("data_object", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="processing_assignments", to="processing.retentiondataobject")),
                ("processing_activity", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="retention_assignments", to="processing.processingactivity")),
                ("storage_system", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="processing_assignments", to="processing.retentionstoragesystem")),
            ],
            options={
                "verbose_name": "Löschzuordnung im Verfahren",
                "verbose_name_plural": "Löschzuordnungen in Verfahren",
                "ordering": ["processing_activity", "sort_order", "data_object__name"],
                "unique_together": {("processing_activity", "data_object", "storage_system")},
            },
        ),
    ]
