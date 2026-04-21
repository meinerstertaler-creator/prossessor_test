from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("processing", "0007_processingactivity_contact_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="processingactivity",
            name="review_status",
            field=models.CharField(blank=True, default="not_started", max_length=20),
        ),
        migrations.AddField(
            model_name="processingactivity",
            name="review_started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]