from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from processing.models import ProcessingActivity
from .forms import DPIAForm, DPIACheckForm, DPIARiskForm, DPIAMeasureForm
from .models import DPIA, DPIACheck, DPIARisk, DPIAMeasure
from .services import close_resolved_dpia_actions, generate_dpia_actions


@login_required
def dpia_detail(request, processing_id):
    processing_activity = get_object_or_404(ProcessingActivity, pk=processing_id)

    dpia, created = DPIA.objects.get_or_create(
        processing_activity=processing_activity
    )
    dpia_check, _ = DPIACheck.objects.get_or_create(
        processing_activity=processing_activity
    )
    legal_record = getattr(processing_activity, "legal_record", None)
    legal_no_dpia_override = bool(
        legal_record and legal_record.no_dpia_check_required_reason
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if legal_no_dpia_override and action in {"save_check", "generate_check_recommendation"}:
            messages.info(
                request,
                "Die DSFA-Prüfung ist gesperrt, weil in der Rechtsbewertung bereits dokumentiert wurde, dass kein DSFA-Check erforderlich ist."
            )
            return redirect("dpia:dpia_detail", processing_id=processing_activity.pk)

        if action == "save_check":
            check_form = DPIACheckForm(request.POST, instance=dpia_check)
            dpia_form = DPIAForm(instance=dpia)
            risk_form = DPIARiskForm()
            measure_form = DPIAMeasureForm()

            if check_form.is_valid():
                dpia_check = check_form.save()
                action_result = generate_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )
                close_resolved_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )

                messages.success(request, "Die DSFA-Prüfung wurde gespeichert.")

                if action_result["created_titles"]:
                    messages.info(
                        request,
                        "Neue Maßnahme(n) hinzugefügt: "
                        + ", ".join(action_result["created_titles"])
                    )

                if action_result["updated_titles"]:
                    messages.info(
                        request,
                        "Bestehende Maßnahme(n) aktualisiert: "
                        + ", ".join(action_result["updated_titles"])
                    )

                return redirect("dpia:dpia_detail", processing_id=processing_activity.pk)

        elif action == "generate_check_recommendation":
            check_form = DPIACheckForm(request.POST, instance=dpia_check)
            dpia_form = DPIAForm(instance=dpia)
            risk_form = DPIARiskForm()
            measure_form = DPIAMeasureForm()

            if check_form.is_valid():
                dpia_check = check_form.save(commit=False)
                dpia_check.reasoning = dpia_check.auto_reasoning_suggestion

                if not (dpia_check.open_points or "").strip():
                    dpia_check.open_points = dpia_check.auto_open_points_suggestion

                dpia_check.save()

                action_result = generate_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )
                close_resolved_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )

                messages.success(request, "Automatische Empfehlung wurde erzeugt.")

                if action_result["created_titles"]:
                    messages.info(
                        request,
                        "Neue Maßnahme(n) hinzugefügt: "
                        + ", ".join(action_result["created_titles"])
                    )

                if action_result["updated_titles"]:
                    messages.info(
                        request,
                        "Bestehende Maßnahme(n) aktualisiert: "
                        + ", ".join(action_result["updated_titles"])
                    )

                return redirect("dpia:dpia_detail", processing_id=processing_activity.pk)

        elif action == "save_dpia":
            check_form = DPIACheckForm(instance=dpia_check)
            dpia_form = DPIAForm(request.POST, instance=dpia)
            risk_form = DPIARiskForm()
            measure_form = DPIAMeasureForm()

            if dpia_form.is_valid():
                dpia = dpia_form.save()
                action_result = generate_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )
                close_resolved_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )

                messages.success(request, "Die DSFA wurde gespeichert.")

                if action_result["created_titles"]:
                    messages.info(
                        request,
                        "Neue Maßnahme(n) hinzugefügt: "
                        + ", ".join(action_result["created_titles"])
                    )

                if action_result["updated_titles"]:
                    messages.info(
                        request,
                        "Bestehende Maßnahme(n) aktualisiert: "
                        + ", ".join(action_result["updated_titles"])
                    )

                return redirect("dpia:dpia_detail", processing_id=processing_activity.pk)

        elif action == "save_dpia_return":
            check_form = DPIACheckForm(instance=dpia_check)
            dpia_form = DPIAForm(request.POST, instance=dpia)
            risk_form = DPIARiskForm()
            measure_form = DPIAMeasureForm()

            if dpia_form.is_valid():
                dpia = dpia_form.save()
                action_result = generate_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )
                close_resolved_dpia_actions(
                    processing_activity=processing_activity,
                    dpia_check=dpia_check,
                    dpia=dpia,
                )

                messages.success(request, "Die DSFA wurde gespeichert.")

                if action_result["created_titles"]:
                    messages.info(
                        request,
                        "Neue Maßnahme(n) hinzugefügt: "
                        + ", ".join(action_result["created_titles"])
                    )

                if action_result["updated_titles"]:
                    messages.info(
                        request,
                        "Bestehende Maßnahme(n) aktualisiert: "
                        + ", ".join(action_result["updated_titles"])
                    )

                return redirect("processing_detail", pk=processing_activity.pk)

        elif action == "add_risk":
            check_form = DPIACheckForm(instance=dpia_check)
            dpia_form = DPIAForm(instance=dpia)
            risk_form = DPIARiskForm(request.POST)
            measure_form = DPIAMeasureForm()

            if risk_form.is_valid():
                risk = risk_form.save(commit=False)
                risk.dpia = dpia
                risk.save()
                messages.success(request, "Das Risiko wurde hinzugefügt.")
                return redirect("dpia:dpia_detail", processing_id=processing_activity.pk)

        elif action == "add_measure":
            check_form = DPIACheckForm(instance=dpia_check)
            dpia_form = DPIAForm(instance=dpia)
            risk_form = DPIARiskForm()
            measure_form = DPIAMeasureForm(request.POST)

            if measure_form.is_valid():
                measure = measure_form.save(commit=False)
                measure.dpia = dpia
                measure.save()
                messages.success(request, "Die Maßnahme wurde hinzugefügt.")
                return redirect("dpia:dpia_detail", processing_id=processing_activity.pk)

        else:
            check_form = DPIACheckForm(instance=dpia_check)
            dpia_form = DPIAForm(instance=dpia)
            risk_form = DPIARiskForm()
            measure_form = DPIAMeasureForm()
    else:
        check_form = DPIACheckForm(instance=dpia_check)
        dpia_form = DPIAForm(instance=dpia)
        risk_form = DPIARiskForm()
        measure_form = DPIAMeasureForm()

    if legal_no_dpia_override:
        for field in check_form.fields.values():
            field.disabled = True

    risks = dpia.risks.all().order_by("title")
    measures = dpia.measures.all().order_by("title")

    context = {
        "processing_activity": processing_activity,
        "dpia": dpia,
        "dpia_check": dpia_check,
        "legal_record": legal_record,
        "check_form": check_form,
        "dpia_form": dpia_form,
        "risk_form": risk_form,
        "measure_form": measure_form,
        "risks": risks,
        "measures": measures,
        "is_new": created,
        "legal_no_dpia_override": legal_no_dpia_override,
    }
    return render(request, "dpia/form.html", context)


@login_required
def dpia_delete_risk(request, pk):
    risk = get_object_or_404(DPIARisk, pk=pk)
    processing_id = risk.dpia.processing_activity.pk

    if request.method == "POST":
        risk.delete()
        messages.success(request, "Das Risiko wurde gelöscht.")

    return redirect("dpia:dpia_detail", processing_id=processing_id)


@login_required
def dpia_delete_measure(request, pk):
    measure = get_object_or_404(DPIAMeasure, pk=pk)
    processing_id = measure.dpia.processing_activity.pk

    if request.method == "POST":
        measure.delete()
        messages.success(request, "Die Maßnahme wurde gelöscht.")

    return redirect("dpia:dpia_detail", processing_id=processing_id)