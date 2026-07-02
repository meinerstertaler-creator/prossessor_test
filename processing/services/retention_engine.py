"""
Retention Engine für PROSSESSOR.

Ziel:
Die Regelermittlung wird aus den Models herausgelöst und als kleine,
testbare Fachlogik bereitgestellt.

Aktueller Stand:
- funktioniert mit dem stabilisierten Retention-Modell:
  RetentionDataObject + RetentionStorageSystem + RetentionRule
- berücksichtigt Löschprofile später automatisch, wenn RetentionRule ein Feld
  retention_profile erhält
- führt keine Datenbankänderungen aus
- ist bewusst defensiv geschrieben

Fachliche Grundregel:
    Löschobjekt + Speicherort/System (+ später Löschprofil) = Löschregel

Hinweis:
Konkrete Systeme wie RA-MICRO, DATEV, Salesforce usw. sollen nicht zwingend
immer eigene Regeln erzwingen. Für nicht bekannte Systeme können generische
Systeme gepflegt werden, z. B.:
- E-Mail-System
- Anwaltssoftware
- Praxissoftware
- CRM
- ERP
- DMS
- Fileserver
- Backup-System
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from django.core.exceptions import FieldDoesNotExist

from processing.models import RetentionRule


@dataclass(frozen=True)
class RetentionResolution:
    """
    Ergebnis der Regelermittlung.

    status:
    - complete: eine eindeutige Regel wurde gefunden
    - check: Regel gefunden, aber requires_review=True
    - incomplete: keine Regel gefunden
    - conflict: mehrere gleichwertige Regeln gefunden
    """

    status: str
    rule: Optional[RetentionRule] = None
    message: str = ""


def model_has_field(model: type, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def find_retention_rule(
    *,
    data_object: Any,
    storage_system: Any,
    retention_profile: Any = None,
) -> RetentionResolution:
    """
    Ermittelt die passende Löschregel.

    Derzeitiger stabiler Stand:
        data_object + storage_system

    Späterer Stand:
        retention_profile + data_object + storage_system

    Wenn RetentionRule.retention_profile noch nicht existiert, wird das Profil
    bewusst ignoriert. Dadurch bleibt die Engine mit dem jetzigen Stand lauffähig.
    """

    if not data_object or not storage_system:
        return RetentionResolution(
            status="incomplete",
            message="Löschobjekt und Speicherort/System müssen angegeben sein.",
        )

    qs = RetentionRule.objects.filter(
        data_object=data_object,
        storage_system=storage_system,
        is_active=True,
    )

    if retention_profile is not None and model_has_field(RetentionRule, "retention_profile"):
        profile_qs = qs.filter(retention_profile=retention_profile)
        if profile_qs.exists():
            qs = profile_qs
        else:
            default_qs = qs.filter(retention_profile__is_default=True)
            if default_qs.exists():
                qs = default_qs
            else:
                qs = qs.filter(retention_profile__isnull=True)

    count = qs.count()

    if count == 0:
        return RetentionResolution(
            status="incomplete",
            message="Keine passende Löschregel gefunden.",
        )

    if count > 1:
        return RetentionResolution(
            status="conflict",
            message="Mehrere passende Löschregeln gefunden. Bitte fachlich prüfen.",
        )

    rule = qs.first()
    if rule.requires_review:
        return RetentionResolution(
            status="check",
            rule=rule,
            message="Passende Löschregel gefunden, aber fachliche Prüfung erforderlich.",
        )

    return RetentionResolution(
        status="complete",
        rule=rule,
        message="Passende Löschregel gefunden.",
    )


def resolve_assignment(assignment: Any) -> RetentionResolution:
    """
    Ermittelt die Regel für eine ProcessingRetentionAssignment-Instanz.

    Diese Funktion verändert die Instanz nicht automatisch. Sie liefert nur das
    Ergebnis. Dadurch kann sie später in Views, Reports oder Save-Logik
    kontrolliert verwendet werden.
    """

    retention_profile = getattr(assignment, "retention_profile", None)

    return find_retention_rule(
        data_object=getattr(assignment, "data_object", None),
        storage_system=getattr(assignment, "storage_system", None),
        retention_profile=retention_profile,
    )
