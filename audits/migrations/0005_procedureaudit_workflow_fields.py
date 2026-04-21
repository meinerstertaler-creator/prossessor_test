from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audits", "0004_remove_procedureaudit_archived_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="procedureaudit",
            name="final_closure_recommended_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="procedureaudit",
            name="new_activities_review_completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="procedureaudit",
            name="preliminary_report_generated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="procedureaudit",
            name="preliminary_report_summary",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="procedureaudit",
            name="procedure_review_completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]