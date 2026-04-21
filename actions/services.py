from actions.models import ActionItem


def _ensure_generated_action_exists(
    *,
    legal_assessment,
    title: str,
    description: str,
    priority: str,
):
    processing = legal_assessment.processing_activity

    exists = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        related_legal_assessment=legal_assessment,
        title=title,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
        ],
    ).exists()

    if exists:
        return None

    return ActionItem.objects.create(
        tenant=processing.tenant,
        title=title,
        description=description,
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        related_processing_activity=processing,
        related_legal_assessment=legal_assessment,
        responsible_person=processing.responsible_person or "",
        priority=priority,
        status=ActionItem.Status.OPEN,
    )


def generate_actions_from_legal_assessment(legal_assessment):
    created_actions = []

    # 1. Offene Punkte
    if legal_assessment.open_issues:
        action = _ensure_generated_action_exists(
            legal_assessment=legal_assessment,
            title="Offene datenschutzrechtliche Punkte klären",
            description=legal_assessment.open_issues,
            priority=ActionItem.Priority.HIGH,
        )
        if action:
            created_actions.append(action)

    # 2. Fehlende / unzureichende Schutzmaßnahmen
    if not (legal_assessment.safeguards or "").strip():
        action = _ensure_generated_action_exists(
            legal_assessment=legal_assessment,
            title="Schutzmaßnahmen konkretisieren",
            description=(
                "Für die rechtliche Bewertung wurden bislang keine ausreichenden "
                "Schutzmaßnahmen dokumentiert. TOM und organisatorische Maßnahmen "
                "sollten konkretisiert und dokumentiert werden."
            ),
            priority=ActionItem.Priority.HIGH,
        )
        if action:
            created_actions.append(action)

    # 3. Kritische oder nicht eindeutige Interessenabwägung
    if (
        legal_assessment.legal_basis == legal_assessment.LegalBasis.LEGITIMATE_INTERESTS
        and legal_assessment.legitimate_interest_outcome
        and legal_assessment.legitimate_interest_outcome
        != legal_assessment.LegitimateInterestOutcome.CONTROLLER
    ):
        action = _ensure_generated_action_exists(
            legal_assessment=legal_assessment,
            title="Interessenabwägung nachschärfen",
            description=(
                "Die dokumentierte Interessenabwägung ist nicht eindeutig zugunsten "
                "des Verantwortlichen ausgefallen. "
                "Begründung:\n\n"
                f"{legal_assessment.legitimate_interest_reasoning or 'Keine Begründung vorhanden.'}"
            ),
            priority=ActionItem.Priority.HIGH,
        )
        if action:
            created_actions.append(action)

    # 4. DSFA erforderlich, aber nicht abgeschlossen
    if legal_assessment.dpia_required and not legal_assessment.processing_activity.dpia_completed:
        action = _ensure_generated_action_exists(
            legal_assessment=legal_assessment,
            title="Datenschutz-Folgenabschätzung durchführen",
            description=(
                "In der Rechtsbewertung wurde ein DSFA-Bedarf erkannt. "
                "Die DSFA ist für den zugehörigen Verarbeitungsvorgang noch nicht "
                "als abgeschlossen dokumentiert."
            ),
            priority=ActionItem.Priority.HIGH,
        )
        if action:
            created_actions.append(action)

    # 5. Interessenabwägung noch nicht abgeschlossen
    if (
        legal_assessment.legal_basis == legal_assessment.LegalBasis.LEGITIMATE_INTERESTS
        and not legal_assessment.legitimate_interest_completed
    ):
        action = _ensure_generated_action_exists(
            legal_assessment=legal_assessment,
            title="Interessenabwägung vervollständigen",
            description=(
                "Die Verarbeitung stützt sich auf Art. 6 Abs. 1 lit. f DSGVO, "
                "aber die Interessenabwägung ist noch nicht abgeschlossen."
            ),
            priority=ActionItem.Priority.MEDIUM,
        )
        if action:
            created_actions.append(action)

    return created_actions