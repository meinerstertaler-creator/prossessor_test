from django.conf import settings
from django.db import models


class AuditLogEntry(models.Model):
    class Action(models.TextChoices):
        CREATED = 'created', 'Erstellt'
        UPDATED = 'updated', 'Geändert'
        DELETED = 'deleted', 'Gelöscht'
        STATUS_CHANGED = 'status_changed', 'Status geändert'
        DOCUMENT_UPLOADED = 'document_uploaded', 'Dokument hochgeladen'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=30, choices=Action.choices)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.object_type} #{self.object_id} – {self.get_action_display()}'
