from actions.models import ActionItem
from .models import Department, ProcessingActivity, ProcessingTemplate, TenantProcessingTemplateSetting


def _is_blank_text(value):
    return not (value or "").strip()


def _reopen_processing_actions(processing_activity):
    ActionItem.objects.filter(
        source_type=ActionItem.SourceType.PROCESSING,
        related_processing_activity=processing_activity,
        status=ActionItem.Status.IRRELEVANT,
    ).update(status=ActionItem.Status.OPEN)


def ensure_processing_action_exists(
    *,
    processing_activity,
    title: str,
    description: str,
    priority: str,
    target_area: str = ActionItem.Area.PROCESSING,
):
    existing_action = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.PROCESSING,
        related_processing_activity=processing_activity,
        title=title,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
            ActionItem.Status.IRRELEVANT,
        ],
    ).first()

    if existing_action:
        changed = False

        if existing_action.description != description:
            existing_action.description = description
            changed = True

        if existing_action.priority != priority:
            existing_action.priority = priority
            changed = True

        if existing_action.source_area != ActionItem.Area.PROCESSING:
            existing_action.source_area = ActionItem.Area.PROCESSING
            changed = True

        if existing_action.target_area != target_area:
            existing_action.target_area = target_area
            changed = True

        responsible_person = processing_activity.responsible_person or ""
        if existing_action.responsible_person != responsible_person:
            existing_action.responsible_person = responsible_person
            changed = True

        if existing_action.status == ActionItem.Status.IRRELEVANT:
            existing_action.status = ActionItem.Status.OPEN
            changed = True

        if changed:
            existing_action.save()

        return existing_action, False, changed

    new_action = ActionItem.objects.create(
        tenant=processing_activity.tenant,
        title=title,
        description=description,
        source_type=ActionItem.SourceType.PROCESSING,
        source_area=ActionItem.Area.PROCESSING,
        target_area=target_area,
        related_processing_activity=processing_activity,
        responsible_person=processing_activity.responsible_person or "",
        priority=priority,
        status=ActionItem.Status.OPEN,
    )

    return new_action, True, False


def generate_processing_actions(processing_activity):
    result = {
        "created_count": 0,
        "updated_count": 0,
        "created_titles": [],
        "updated_titles": [],
    }

    if processing_activity.status == ProcessingActivity.Status.ARCHIVED:
        return result

    if processing_activity.department is None:
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Fachbereich" auswählen',
            description=(
                'Im Verfahren ist das Feld "Fachbereich" noch nicht gesetzt. '
                "Bitte den zuständigen Fachbereich auswählen."
            ),
            priority=ActionItem.Priority.MEDIUM,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.responsible_person):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Verantwortliche Person" ausfüllen',
            description=(
                'Im Verfahren ist das Feld "Verantwortliche Person" noch leer. '
                "Bitte die verantwortliche Person ergänzen."
            ),
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if processing_activity.review_status != processing_activity.ReviewStatus.COMPLETED:
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Bewertungsstatus" auf "Abgeschlossen" setzen',
            description=(
                'Im Verfahren steht das Feld "Bewertungsstatus" noch nicht auf '
                '"Abgeschlossen". Bitte die Bewertung vervollständigen.'
            ),
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if processing_activity.third_party_info_required:
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Checkbox "Drittinformationen erforderlich" auflösen',
            description=(
                'Im Verfahren ist die Checkbox "Drittinformationen erforderlich" gesetzt. '
                "Bitte die fehlenden Drittinformationen einholen und das Verfahren aktualisieren."
            ),
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.purpose):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Zweck der Verarbeitung" ausfüllen',
            description='Im Verfahren ist das Feld "Zweck der Verarbeitung" noch leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.description):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Beschreibung" ausfüllen',
            description='Im Verfahren ist das Feld "Beschreibung" noch leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.data_subject_categories):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Betroffene Personen" ausfüllen',
            description='Im Verfahren ist das Feld "Betroffene Personen" noch leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.personal_data_categories):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Kategorien personenbezogener Daten" ausfüllen',
            description='Im Verfahren ist das Feld "Kategorien personenbezogener Daten" noch leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if (
        processing_activity.special_category_data
        and _is_blank_text(processing_activity.special_category_description)
    ):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Beschreibung besonderer Daten" ausfüllen',
            description='Besondere Kategorien sind markiert, aber die Beschreibung ist leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.systems_used):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Eingesetzte Systeme / Software" ausfüllen',
            description='Im Verfahren ist das Feld "Eingesetzte Systeme / Software" noch leer.',
            priority=ActionItem.Priority.MEDIUM,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.recipients):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Empfänger / Empfängerkategorien" ausfüllen',
            description='Im Verfahren ist das Feld "Empfänger / Empfängerkategorien" noch leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if (
        processing_activity.third_country_transfer
        and _is_blank_text(processing_activity.third_country_description)
    ):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Beschreibung Drittlandtransfer" ausfüllen',
            description='Drittlandtransfer ist markiert, aber die Beschreibung ist leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if _is_blank_text(processing_activity.tom_summary):
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='Feld "Technische und organisatorische Maßnahmen (TOM)" ausfüllen',
            description='Im Verfahren ist das Feld "TOM" noch leer.',
            priority=ActionItem.Priority.HIGH,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if processing_activity.dpia_required and not processing_activity.dpia_completed:
        action, created, updated = ensure_processing_action_exists(
            processing_activity=processing_activity,
            title='DSFA-Status prüfen und Feld "DSFA durchgeführt" setzen',
            description='Für das Verfahren ist eine DSFA erforderlich, aber noch nicht durchgeführt.',
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.DPIA,
        )
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    return result


def _close_processing_action_if_exists(processing_activity, title: str):
    ActionItem.objects.filter(
        source_type=ActionItem.SourceType.PROCESSING,
        related_processing_activity=processing_activity,
        title=title,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
        ],
    ).update(status=ActionItem.Status.COMPLETED)


def _mark_processing_actions_irrelevant(processing_activity):
    ActionItem.objects.filter(
        source_type=ActionItem.SourceType.PROCESSING,
        related_processing_activity=processing_activity,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
            ActionItem.Status.COMPLETED,
        ],
    ).update(status=ActionItem.Status.IRRELEVANT)


def close_resolved_processing_actions(processing_activity):
    if processing_activity.status == ProcessingActivity.Status.ARCHIVED:
        _mark_processing_actions_irrelevant(processing_activity)
        return

    if processing_activity.department is not None:
        _close_processing_action_if_exists(processing_activity, 'Feld "Fachbereich" auswählen')

    if not _is_blank_text(processing_activity.responsible_person):
        _close_processing_action_if_exists(processing_activity, 'Feld "Verantwortliche Person" ausfüllen')

    if processing_activity.review_status == processing_activity.ReviewStatus.COMPLETED:
        _close_processing_action_if_exists(
            processing_activity,
            'Feld "Bewertungsstatus" auf "Abgeschlossen" setzen',
        )

    if not processing_activity.third_party_info_required:
        _close_processing_action_if_exists(
            processing_activity,
            'Checkbox "Drittinformationen erforderlich" auflösen',
        )

    if not _is_blank_text(processing_activity.purpose):
        _close_processing_action_if_exists(processing_activity, 'Feld "Zweck der Verarbeitung" ausfüllen')

    if not _is_blank_text(processing_activity.description):
        _close_processing_action_if_exists(processing_activity, 'Feld "Beschreibung" ausfüllen')

    if not _is_blank_text(processing_activity.data_subject_categories):
        _close_processing_action_if_exists(processing_activity, 'Feld "Betroffene Personen" ausfüllen')

    if not _is_blank_text(processing_activity.personal_data_categories):
        _close_processing_action_if_exists(
            processing_activity,
            'Feld "Kategorien personenbezogener Daten" ausfüllen',
        )

    if (
        not processing_activity.special_category_data
        or not _is_blank_text(processing_activity.special_category_description)
    ):
        _close_processing_action_if_exists(
            processing_activity,
            'Feld "Beschreibung besonderer Daten" ausfüllen',
        )

    if not _is_blank_text(processing_activity.systems_used):
        _close_processing_action_if_exists(
            processing_activity,
            'Feld "Eingesetzte Systeme / Software" ausfüllen',
        )

    if not _is_blank_text(processing_activity.recipients):
        _close_processing_action_if_exists(
            processing_activity,
            'Feld "Empfänger / Empfängerkategorien" ausfüllen',
        )

    if (
        not processing_activity.third_country_transfer
        or not _is_blank_text(processing_activity.third_country_description)
    ):
        _close_processing_action_if_exists(
            processing_activity,
            'Feld "Beschreibung Drittlandtransfer" ausfüllen',
        )

    if not _is_blank_text(processing_activity.tom_summary):
        _close_processing_action_if_exists(
            processing_activity,
            'Feld "Technische und organisatorische Maßnahmen (TOM)" ausfüllen',
        )

    if not processing_activity.dpia_required or processing_activity.dpia_completed:
        _close_processing_action_if_exists(
            processing_activity,
            'DSFA-Status prüfen und Feld "DSFA durchgeführt" setzen',
        )


def _resolve_department_for_template(*, tenant, template):
    if tenant is None or not template.department:
        return None

    return Department.objects.filter(
        tenant=tenant,
        name__iexact=template.department.strip(),
    ).first()


def create_processing_activity_from_template(*, tenant, template, user=None):
    department = _resolve_department_for_template(tenant=tenant, template=template)

    item = ProcessingActivity(
        tenant=tenant,
        title=template.title,
        department=department,
        template_origin=template,
        purpose=template.purpose,
        description=template.description,
        data_subject_categories=template.data_subject_categories,
        personal_data_categories=template.personal_data_categories,
        recipients=template.recipients,
        retention_period=template.retention_period,
        tom_summary=template.tom_summary,
        created_by=user,
        updated_by=user,
    )
    item.save()

    action_result = generate_processing_actions(item)
    close_resolved_processing_actions(item)

    return item, action_result


def sync_tenant_processing_templates(*, tenant, user=None):
    templates = ProcessingTemplate.objects.filter(is_active=True).order_by("template_group", "title")

    for template in templates:
        setting, _created = TenantProcessingTemplateSetting.objects.get_or_create(
            tenant=tenant,
            template=template,
            defaults={"is_enabled": True},
        )

        if not setting.is_enabled:
            continue

        exists = ProcessingActivity.objects.filter(
            tenant=tenant,
            template_origin=template,
        ).exists()

        if exists:
            continue

        create_processing_activity_from_template(
            tenant=tenant,
            template=template,
            user=user,
        )


def archive_processing_activity(*, processing_activity, user=None):
    processing_activity.status = ProcessingActivity.Status.ARCHIVED
    processing_activity.updated_by = user
    processing_activity.archived_by = user
    processing_activity.save()
    close_resolved_processing_actions(processing_activity)
    return processing_activity


def reactivate_processing_activity(*, processing_activity, user=None):
    processing_activity.status = ProcessingActivity.Status.ACTIVE
    processing_activity.updated_by = user
    processing_activity.archived_by = None
    processing_activity.archived_at = None
    processing_activity.save()

    _reopen_processing_actions(processing_activity)

    action_result = generate_processing_actions(processing_activity)
    close_resolved_processing_actions(processing_activity)
    return processing_activity, action_result