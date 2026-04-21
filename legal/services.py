from actions.models import ActionItem


def _is_blank_text(value):
    return not (value or "").strip()


def ensure_action_exists(
    *,
    assessment,
    title: str,
    description: str,
    priority: str,
    target_area: str = ActionItem.Area.LEGAL,
):
    processing = assessment.processing_activity

    existing_action = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        related_legal_assessment=assessment,
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

        if existing_action.source_area != ActionItem.Area.LEGAL:
            existing_action.source_area = ActionItem.Area.LEGAL
            changed = True

        if existing_action.target_area != target_area:
            existing_action.target_area = target_area
            changed = True

        responsible_person = processing.responsible_person or ""
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
        tenant=processing.tenant,
        title=title,
        description=description,
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        source_area=ActionItem.Area.LEGAL,
        target_area=target_area,
        related_processing_activity=processing,
        related_legal_assessment=assessment,
        responsible_person=processing.responsible_person or "",
        priority=priority,
        status=ActionItem.Status.OPEN,
    )

    return new_action, True, False


def generate_legal_assessment_actions(assessment):
    processing = assessment.processing_activity

    result = {
        "created_count": 0,
        "updated_count": 0,
    }

    if _is_blank_text(assessment.legal_assessment_text):
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title='Feld "Juristische Bewertung" ausfüllen',
            description=(
                'In der Rechtsbewertung ist das Feld "Juristische Bewertung" noch leer. '
                "Bitte die textliche Rechtsbewertung eintragen."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if not assessment.legal_basis:
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="Rechtsgrundlage prüfen",
            description=(
                "Für diesen Verarbeitungsvorgang wurde noch keine Rechtsgrundlage "
                "nach Art. 6 DSGVO dokumentiert."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if processing.special_category_data and not assessment.special_legal_basis:
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="Art.-9-Rechtsgrundlage klären",
            description=(
                "Es werden besondere Kategorien personenbezogener Daten verarbeitet, "
                "aber es wurde noch keine Rechtsgrundlage nach Art. 9 DSGVO dokumentiert."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if (
        assessment.legal_basis == assessment.LegalBasis.LEGITIMATE_INTERESTS
        and not assessment.legitimate_interest_completed
    ):
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="Interessenabwägung durchführen",
            description=(
                "Die Verarbeitung stützt sich auf berechtigte Interessen, "
                "aber die erforderliche Interessenabwägung ist noch nicht als abgeschlossen dokumentiert."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if assessment.professional_secrecy and not assessment.section_203_process_implemented:
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="203er Verfahren implementieren",
            description=(
                "Für dieses Verfahren ist Berufsgeheimnis / § 203 StGB als relevant markiert. "
                "Ein 203er Verfahren ist noch nicht als implementiert dokumentiert. "
                "Bitte prüfen und dokumentieren, wie die erforderliche Vertraulichkeitsabsicherung "
                "für die betroffenen Personengruppen und eingebundenen Stellen umgesetzt wird."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if processing.third_country_transfer and not assessment.open_issues:
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="Drittlandtransfer rechtlich prüfen",
            description=(
                "Es liegt ein Drittlandtransfer vor. Die rechtliche Bewertung "
                "und Dokumentation des Transfermechanismus sollte geprüft werden."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    dpia_check = getattr(processing, "dpia_check", None)

    if not dpia_check and not assessment.no_dpia_check_required_reason:
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="DSFA-Check durchführen oder Entbehrlichkeit dokumentieren",
            description=(
                "Es liegt weder ein Ergebnis der DSFA-Prüfung vor noch ist dokumentiert, "
                "warum kein gesonderter DSFA-Check erforderlich ist."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if (
        assessment.no_dpia_check_required_reason == assessment.NoDPIACheckReason.OTHER
        and _is_blank_text(assessment.no_dpia_check_required_note)
    ):
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="Begründung für entbehrlichen DSFA-Check ergänzen",
            description=(
                "Für den entbehrlichen DSFA-Check wurde 'Sonstiger Grund' gewählt, "
                "aber die ergänzende Begründung fehlt noch."
            ),
            priority=ActionItem.Priority.MEDIUM,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if dpia_check and dpia_check.recommendation == "mandatory":
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="DSFA durchführen",
            description=(
                "Die DSFA-Prüfung ergibt, dass eine DSFA erforderlich ist. "
                "Bitte die DSFA-Durchführung vervollständigen."
            ),
            priority=ActionItem.Priority.HIGH,
            target_area=ActionItem.Area.DPIA,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    if assessment.open_issues:
        _, created, updated = ensure_action_exists(
            assessment=assessment,
            title="Offene Rechtsfragen klären",
            description=(
                "In der Rechtsbewertung wurden offene Rechtsfragen oder Klärungspunkte dokumentiert. "
                "Diese sollten geprüft und bearbeitet werden.\n\n"
                f"Offene Punkte:\n{assessment.open_issues}"
            ),
            priority=ActionItem.Priority.MEDIUM,
            target_area=ActionItem.Area.LEGAL,
        )
        if created:
            result["created_count"] += 1
        if updated:
            result["updated_count"] += 1

    return result


def _close_action_if_exists(assessment, title: str):
    ActionItem.objects.filter(
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        related_legal_assessment=assessment,
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


def _mark_action_irrelevant_if_exists(assessment, title: str):
    ActionItem.objects.filter(
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        related_legal_assessment=assessment,
        title=title,
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


def close_resolved_legal_assessment_actions(assessment):
    processing = assessment.processing_activity
    dpia_check = getattr(processing, "dpia_check", None)

    if not _is_blank_text(assessment.legal_assessment_text):
        _close_action_if_exists(
            assessment,
            'Feld "Juristische Bewertung" ausfüllen',
        )

    if assessment.legal_basis:
        _close_action_if_exists(
            assessment,
            "Rechtsgrundlage prüfen",
        )

    if not processing.special_category_data or assessment.special_legal_basis:
        _close_action_if_exists(
            assessment,
            "Art.-9-Rechtsgrundlage klären",
        )

    if (
        assessment.legal_basis == assessment.LegalBasis.LEGITIMATE_INTERESTS
        and assessment.legitimate_interest_completed
    ):
        _close_action_if_exists(
            assessment,
            "Interessenabwägung durchführen",
        )

    if assessment.professional_secrecy and assessment.section_203_process_implemented:
        _mark_action_irrelevant_if_exists(
            assessment,
            "203er Verfahren implementieren",
        )
    elif not assessment.professional_secrecy:
        _mark_action_irrelevant_if_exists(
            assessment,
            "203er Verfahren implementieren",
        )

    if not processing.third_country_transfer or (assessment.open_issues or "").strip():
        _close_action_if_exists(
            assessment,
            "Drittlandtransfer rechtlich prüfen",
        )

    if dpia_check or assessment.no_dpia_check_required_reason:
        _close_action_if_exists(
            assessment,
            "DSFA-Check durchführen oder Entbehrlichkeit dokumentieren",
        )

    if (
        assessment.no_dpia_check_required_reason != assessment.NoDPIACheckReason.OTHER
        or not _is_blank_text(assessment.no_dpia_check_required_note)
    ):
        _close_action_if_exists(
            assessment,
            "Begründung für entbehrlichen DSFA-Check ergänzen",
        )

    if not dpia_check or dpia_check.recommendation != "mandatory":
        _close_action_if_exists(
            assessment,
            "DSFA durchführen",
        )

    if not (assessment.open_issues or "").strip():
        _close_action_if_exists(
            assessment,
            "Offene Rechtsfragen klären",
        )


def apply_ai_result_to_assessment(assessment, ai_result, topic):
    if topic == "legitimate_interest":
        assessment.legitimate_interest_purpose = ai_result.get("purpose", "")
        assessment.data_subject_impact = ai_result.get("impact", "")
        assessment.safeguards = ai_result.get("safeguards", "")
        assessment.legitimate_interest_reasoning = ai_result.get("reasoning", "")

        outcome = ai_result.get("outcome")
        if outcome == "controller":
            assessment.legitimate_interest_outcome = (
                assessment.LegitimateInterestOutcome.CONTROLLER
            )
        elif outcome == "balanced":
            assessment.legitimate_interest_outcome = (
                assessment.LegitimateInterestOutcome.BALANCED
            )
        elif outcome == "data_subject":
            assessment.legitimate_interest_outcome = (
                assessment.LegitimateInterestOutcome.DATA_SUBJECT
            )

        assessment.legitimate_interest_test = True
        assessment.legitimate_interest_completed = True

        outcome_label = "Interessen des Verantwortlichen überwiegen"
        if assessment.legitimate_interest_outcome == assessment.LegitimateInterestOutcome.BALANCED:
            outcome_label = "Abwägung ausgeglichen / vertretbar"
        elif assessment.legitimate_interest_outcome == assessment.LegitimateInterestOutcome.DATA_SUBJECT:
            outcome_label = "Interessen der betroffenen Person überwiegen"

        assessment.legal_assessment_text = (
            "Interessenabwägung (automatisch erstellt):\n\n"
            f"1. Berechtigtes Interesse des Verantwortlichen:\n"
            f"{assessment.legitimate_interest_purpose}\n\n"
            f"2. Auswirkungen auf die betroffene Person:\n"
            f"{assessment.data_subject_impact}\n\n"
            f"3. Schutzmaßnahmen:\n"
            f"{assessment.safeguards}\n\n"
            f"4. Begründung der Abwägung:\n"
            f"{assessment.legitimate_interest_reasoning}\n\n"
            f"5. Ergebnis:\n{outcome_label}"
        )

    elif topic == "legal_assessment":
        assessment.legal_assessment_text = ai_result.get("text", "")