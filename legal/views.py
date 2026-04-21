from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from actions.models import ActionItem
from dpia.models import DPIA, DPIACheck
from dpia.services import close_resolved_dpia_actions, generate_dpia_actions
from processing.models import ProcessingActivity

from .forms import LegalAssessmentForm
from .models import LegalAssessment
from .services import (
    apply_ai_result_to_assessment,
    close_resolved_legal_assessment_actions,
    generate_legal_assessment_actions,
)
from knowledge.ai_engine import generate_ai_structured_output
from knowledge.ai_services import build_ai_context_bundle, build_ai_prompt_stub


def _ensure_dpia_reactivation_action(*, processing_activity, legal_assessment):
    title = "DSFA-Prüfung erneut durchführen"

    existing = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        related_legal_assessment=legal_assessment,
        related_processing_activity=processing_activity,
        title=title,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
        ],
    ).first()

    if existing:
        return None

    return ActionItem.objects.create(
        tenant=processing_activity.tenant,
        title=title,
        description=(
            "Die zuvor dokumentierte Entscheidung, dass kein DSFA-Check erforderlich ist, "
            "wurde aufgehoben. Die DSFA-Prüfung ist erneut zu bewerten und bei Bedarf "
            "weiterzuführen."
        ),
        source_type=ActionItem.SourceType.LEGAL_ASSESSMENT,
        source_area=ActionItem.Area.LEGAL,
        target_area=ActionItem.Area.DPIA,
        related_processing_activity=processing_activity,
        related_legal_assessment=legal_assessment,
        responsible_person=processing_activity.responsible_person or "",
        priority=ActionItem.Priority.HIGH,
        status=ActionItem.Status.OPEN,
    )


@login_required
def legal_assessment_upsert(request, processing_id):
    processing_activity = get_object_or_404(ProcessingActivity, pk=processing_id)

    legal_assessment, created = LegalAssessment.objects.get_or_create(
        processing_activity=processing_activity,
        defaults={"tenant": processing_activity.tenant},
    )

    dpia_check = getattr(processing_activity, "dpia_check", None)
    dpia = getattr(processing_activity, "dpia", None)

    if dpia is None:
        dpia = DPIA.objects.create(processing_activity=processing_activity)

    if dpia_check is None:
        dpia_check = DPIACheck.objects.create(processing_activity=processing_activity)

    if request.method == "POST":
        old_reason = (legal_assessment.no_dpia_check_required_reason or "").strip()

        form = LegalAssessmentForm(
            request.POST,
            instance=legal_assessment,
            processing_activity=processing_activity,
        )

        if form.is_valid():
            assessment = form.save(commit=False)
            new_reason = (assessment.no_dpia_check_required_reason or "").strip()

            override_removed = bool(old_reason and not new_reason)
            confirm_flag = request.POST.get("confirm_remove_dpia_override") == "1"

            if override_removed and not confirm_flag:
                messages.warning(
                    request,
                    "Bitte bestätige die Aufhebung der DSFA-Ausnahme durch Anhaken der Bestätigungsbox."
                )
                return render(
                    request,
                    "legal/legal_assessment_form.html",
                    {
                        "processing_activity": processing_activity,
                        "legal_assessment": legal_assessment,
                        "dpia_check": dpia_check,
                        "form": form,
                        "is_new": created,
                        "force_show_dpia_override_edit": True,
                    },
                )

            if not assessment.tenant_id:
                assessment.tenant = processing_activity.tenant

            if dpia_check and dpia_check.has_must_list_case:
                assessment.no_dpia_check_required_reason = ""
                assessment.no_dpia_check_required_note = ""

            action = request.POST.get("action")

            if action == "generate_ai":
                assessment.save()

                topic = "legal_assessment"
                target_label = "Juristische Bewertung"

                if assessment.legal_basis == LegalAssessment.LegalBasis.LEGITIMATE_INTERESTS:
                    topic = "legitimate_interest"
                    target_label = "Interessenabwägung"

                context_bundle = build_ai_context_bundle(
                    topic=topic,
                    processing_activity=processing_activity,
                    legal_assessment=assessment,
                )

                prompt = build_ai_prompt_stub(
                    topic=topic,
                    target_label=target_label,
                    processing_activity=processing_activity,
                    legal_assessment=assessment,
                )

                assessment.ai_prompt = prompt
                assessment.ai_prompt_version = "v1"
                assessment.save()

                try:
                    ai_result = generate_ai_structured_output(topic, context_bundle)

                    apply_ai_result_to_assessment(assessment, ai_result, topic)

                    if topic == "legal_assessment":
                        assessment.ai_suggestion = ai_result.get("text", "") or ai_result.get(
                            "ai_suggestion", ""
                        )
                    else:
                        assessment.ai_suggestion = assessment.legal_assessment_text

                    if dpia_check and dpia_check.has_must_list_case:
                        assessment.no_dpia_check_required_reason = ""
                        assessment.no_dpia_check_required_note = ""

                    assessment.save()

                    action_result = generate_legal_assessment_actions(assessment)
                    close_resolved_legal_assessment_actions(assessment)

                    generate_dpia_actions(
                        processing_activity=processing_activity,
                        dpia_check=dpia_check,
                        dpia=dpia,
                    )
                    close_resolved_dpia_actions(
                        processing_activity=processing_activity,
                        dpia_check=dpia_check,
                        dpia=dpia,
                    )

                    messages.success(request, "Der KI-Vorschlag wurde erzeugt.")

                    if action_result["created_count"] > 0:
                        messages.info(
                            request,
                            f"{action_result['created_count']} neue Maßnahme(n) wurden hinzugefügt."
                        )

                    if action_result["updated_count"] > 0:
                        messages.info(
                            request,
                            f"{action_result['updated_count']} bestehende Maßnahme(n) wurden aktualisiert."
                        )

                except Exception as exc:
                    messages.error(
                        request,
                        f"Beim Erzeugen des KI-Vorschlags ist ein Fehler aufgetreten: {exc}"
                    )

                return redirect("legal_assessment_edit", processing_id=processing_activity.pk)

            assessment.save()

            reactivation_action = None
            if override_removed:
                reactivation_action = _ensure_dpia_reactivation_action(
                    processing_activity=processing_activity,
                    legal_assessment=assessment,
                )

            action_result = generate_legal_assessment_actions(assessment)
            close_resolved_legal_assessment_actions(assessment)

            generate_dpia_actions(
                processing_activity=processing_activity,
                dpia_check=dpia_check,
                dpia=dpia,
            )
            close_resolved_dpia_actions(
                processing_activity=processing_activity,
                dpia_check=dpia_check,
                dpia=dpia,
            )

            messages.success(request, "Die Rechtsbewertung wurde gespeichert.")

            if action_result["created_count"] > 0:
                messages.info(
                    request,
                    f"{action_result['created_count']} neue Maßnahme(n) wurden hinzugefügt."
                )

            if action_result["updated_count"] > 0:
                messages.info(
                    request,
                    f"{action_result['updated_count']} bestehende Maßnahme(n) wurden aktualisiert."
                )

            if override_removed:
                messages.warning(
                    request,
                    "Die dokumentierte DSFA-Ausnahme wurde aufgehoben. Die DSFA-Prüfung ist wieder aktiv."
                )
                if reactivation_action is not None:
                    messages.warning(
                        request,
                        "Es wurde automatisch eine Maßnahme zur erneuten DSFA-Prüfung angelegt."
                    )
                else:
                    messages.info(
                        request,
                        "Eine passende offene Maßnahme zur erneuten DSFA-Prüfung war bereits vorhanden."
                    )

            if action == "save_and_return":
                return redirect("processing_detail", pk=processing_activity.pk)

            return redirect("legal_assessment_edit", processing_id=processing_activity.pk)

    else:
        form = LegalAssessmentForm(
            instance=legal_assessment,
            processing_activity=processing_activity,
        )

    return render(
        request,
        "legal/legal_assessment_form.html",
        {
            "processing_activity": processing_activity,
            "legal_assessment": legal_assessment,
            "dpia_check": dpia_check,
            "form": form,
            "is_new": created,
            "force_show_dpia_override_edit": False,
        },
    )