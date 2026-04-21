from actions.models import ActionItem


def _is_blank_text(value):
    return not (value or "").strip()


def _has_legal_no_dpia_override(processing_activity):
    legal_record = getattr(processing_activity, "legal_record", None)
    return bool(legal_record and legal_record.no_dpia_check_required_reason)


def ensure_dpia_action_exists(
    *,
    processing_activity,
    title: str,
    description: str,
    priority: str,
):
    existing_action = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.DPIA,
        related_processing_activity=processing_activity,
        title=title,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
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

        if existing_action.source_area != ActionItem.Area.DPIA:
            existing_action.source_area = ActionItem.Area.DPIA
            changed = True

        if existing_action.target_area != ActionItem.Area.DPIA:
            existing_action.target_area = ActionItem.Area.DPIA
            changed = True

        responsible_person = processing_activity.responsible_person or ""
        if existing_action.responsible_person != responsible_person:
            existing_action.responsible_person = responsible_person
            changed = True

        if changed:
            existing_action.save()

        return existing_action, False, changed

    new_action = ActionItem.objects.create(
        tenant=processing_activity.tenant,
        title=title,
        description=description,
        source_type=ActionItem.SourceType.DPIA,
        source_area=ActionItem.Area.DPIA,
        target_area=ActionItem.Area.DPIA,
        related_processing_activity=processing_activity,
        responsible_person=processing_activity.responsible_person or "",
        priority=priority,
        status=ActionItem.Status.OPEN,
    )

    return new_action, True, False


def generate_dpia_actions(*, processing_activity, dpia_check, dpia):
    result = {
        "created_count": 0,
        "updated_count": 0,
        "created_titles": [],
        "updated_titles": [],
    }

    if _has_legal_no_dpia_override(processing_activity):
        return result

    def _handle(action_tuple):
        action, created, updated = action_tuple
        if created:
            result["created_count"] += 1
            result["created_titles"].append(action.title)
        if updated:
            result["updated_count"] += 1
            result["updated_titles"].append(action.title)

    if dpia_check.recommendation == "not_checked":
        return result

    if _is_blank_text(dpia_check.reasoning):
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA-Prüfung: Begründung ergänzen",
                description=(
                    "In der DSFA-Prüfung fehlt noch eine Begründung für die Einschätzung "
                    "der DSFA-Relevanz bzw. des Risikoniveaus."
                ),
                priority=ActionItem.Priority.HIGH,
            )
        )

    if not _is_blank_text(dpia_check.open_points):
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA-Prüfung: offene Punkte klären",
                description=(
                    "In der DSFA-Prüfung wurden offene Punkte dokumentiert. "
                    "Diese sollten fachlich geklärt und bearbeitet werden.\n\n"
                    f"Offene Punkte:\n{dpia_check.open_points}"
                ),
                priority=ActionItem.Priority.HIGH,
            )
        )

    if dpia_check.recommendation in {"mandatory", "recommended"} and not dpia_check.completed:
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA-Prüfung abschließen",
                description=(
                    "Die DSFA-Prüfung ist noch nicht als abgeschlossen markiert, obwohl "
                    "eine DSFA erforderlich oder empfohlen ist."
                ),
                priority=ActionItem.Priority.HIGH,
            )
        )

    if dpia_check.recommendation in {"mandatory", "recommended"} and not dpia.approved:
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA durchführen",
                description=(
                    "Die DSFA-Prüfung ergibt, dass eine DSFA erforderlich oder empfohlen ist. "
                    "Die DSFA-Durchführung ist jedoch noch nicht freigegeben."
                ),
                priority=ActionItem.Priority.HIGH,
            )
        )

    if dpia_check.recommendation in {"mandatory", "recommended"} and _is_blank_text(dpia.description):
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA-Durchführung: Beschreibung ergänzen",
                description=(
                    "In der DSFA-Durchführung fehlt noch die Beschreibung der Verarbeitung."
                ),
                priority=ActionItem.Priority.HIGH,
            )
        )

    if dpia_check.recommendation in {"mandatory", "recommended"} and _is_blank_text(dpia.necessity_assessment):
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA-Durchführung: Notwendigkeit und Verhältnismäßigkeit ergänzen",
                description=(
                    "In der DSFA-Durchführung fehlt noch die Bewertung von "
                    "Notwendigkeit und Verhältnismäßigkeit."
                ),
                priority=ActionItem.Priority.HIGH,
            )
        )

    if dpia_check.recommendation in {"mandatory", "recommended"} and _is_blank_text(dpia.result_summary):
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA-Durchführung: Ergebnis ergänzen",
                description=(
                    "In der DSFA-Durchführung fehlt noch die Zusammenfassung bzw. das Ergebnis."
                ),
                priority=ActionItem.Priority.HIGH,
            )
        )

    if dpia_check.recommendation in {"mandatory", "recommended"} and _is_blank_text(dpia.residual_risk):
        _handle(
            ensure_dpia_action_exists(
                processing_activity=processing_activity,
                title="DSFA-Durchführung: Restrisiko ergänzen",
                description=(
                    "In der DSFA-Durchführung fehlt noch die Angabe zum Restrisiko."
                ),
                priority=ActionItem.Priority.MEDIUM,
            )
        )

    return result


def _close_dpia_action_if_exists(processing_activity, title: str):
    ActionItem.objects.filter(
        source_type=ActionItem.SourceType.DPIA,
        related_processing_activity=processing_activity,
        title=title,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
        ],
    ).update(
        status=ActionItem.Status.COMPLETED,
    )


def _mark_all_dpia_actions_irrelevant(processing_activity):
    ActionItem.objects.filter(
        source_type=ActionItem.SourceType.DPIA,
        related_processing_activity=processing_activity,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
            ActionItem.Status.COMPLETED,
        ],
    ).update(
        status=ActionItem.Status.IRRELEVANT,
    )


def close_resolved_dpia_actions(*, processing_activity, dpia_check, dpia):
    if _has_legal_no_dpia_override(processing_activity):
        _mark_all_dpia_actions_irrelevant(processing_activity)
        return

    if dpia_check.recommendation == "not_checked":
        return

    if not _is_blank_text(dpia_check.reasoning):
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA-Prüfung: Begründung ergänzen",
        )

    if _is_blank_text(dpia_check.open_points):
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA-Prüfung: offene Punkte klären",
        )

    if dpia_check.completed or dpia_check.recommendation == "not_required":
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA-Prüfung abschließen",
        )

    if dpia.approved or dpia_check.recommendation not in {"mandatory", "recommended"}:
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA durchführen",
        )

    if not _is_blank_text(dpia.description):
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA-Durchführung: Beschreibung ergänzen",
        )

    if not _is_blank_text(dpia.necessity_assessment):
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA-Durchführung: Notwendigkeit und Verhältnismäßigkeit ergänzen",
        )

    if not _is_blank_text(dpia.result_summary):
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA-Durchführung: Ergebnis ergänzen",
        )

    if not _is_blank_text(dpia.residual_risk):
        _close_dpia_action_if_exists(
            processing_activity,
            "DSFA-Durchführung: Restrisiko ergänzen",
        )