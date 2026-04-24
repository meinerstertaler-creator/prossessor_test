from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import File
from django.shortcuts import get_object_or_404, redirect, render

from actions.models import ActionItem
from core.tenant_utils import get_effective_tenant
from documents.models import Document
from .forms import ProcessorForm
from .models import Processor, ProviderCatalogEntry


def _tenant_filtered_processor_queryset(request):
    qs = (
        Processor.objects.select_related(
            "department",
            "catalog_entry",
        )
        .prefetch_related("provider_roles")
        .order_by("name")
    )
    active_tenant = get_effective_tenant(request)

    if request.user.is_superuser:
        if active_tenant is None:
            return qs
        return qs.filter(tenant=active_tenant)

    if request.user.tenant_id:
        return qs.filter(tenant=request.user.tenant)

    return qs.none()


def _get_provider_catalog_payload():
    entries = (
        ProviderCatalogEntry.objects.filter(is_active=True)
        .prefetch_related("roles")
        .order_by("name")
    )

    payload = []
    for entry in entries:
        active_roles = list(entry.roles.filter(is_active=True).order_by("name"))
        payload.append(
            {
                "id": entry.pk,
                "name": entry.name or "",
                "legal_name": entry.legal_name or "",
                "address": entry.address or "",
                "default_contact_person": entry.default_contact_person or "",
                "default_contact_email": entry.default_contact_email or "",
                "website": entry.website or "",
                "standard_av_available": entry.standard_av_available,
                "standard_tom_available": entry.standard_tom_available,
                "notes": entry.notes or "",
                "role_ids": [role.pk for role in active_roles],
                "role_names": [role.name for role in active_roles],
            }
        )
    return payload


def _copy_catalog_file_to_document(*, processor, source_field, document_type, title):
    if not source_field:
        return None

    existing = Document.objects.filter(
        related_processor=processor,
        document_type=document_type,
    ).exists()

    if existing:
        return None

    source_field.open("rb")
    try:
        new_document = Document(
            tenant=processor.tenant,
            related_processor=processor,
            title=title,
            document_type=document_type,
            description="Aus dem Anbieter-Katalog übernommen.",
            origin=Document.DocumentOrigin.GENERATED,
            document_status=Document.DocumentStatus.UNEDITED,
            source_catalog_updated_at=processor.catalog_entry.updated_at if processor.catalog_entry else None,
        )
        new_document.file.save(
            source_field.name.split("/")[-1],
            File(source_field),
            save=False,
        )
        new_document.save()
        return new_document
    finally:
        source_field.close()


def _copy_catalog_documents_to_tenant(processor):
    catalog = processor.catalog_entry
    if not catalog:
        return {"av_created": False, "tom_created": False}

    av_doc = _copy_catalog_file_to_document(
        processor=processor,
        source_field=catalog.standard_av_file,
        document_type=Document.DocumentType.AV_CONTRACT,
        title=f"AV-Vertrag {processor.name} (Standard)",
    )

    tom_doc = _copy_catalog_file_to_document(
        processor=processor,
        source_field=catalog.standard_tom_file,
        document_type=Document.DocumentType.TOM,
        title=f"TOM {processor.name} (Standard)",
    )

    changed = False
    if av_doc and not processor.av_contract_exists:
        processor.av_contract_exists = True
        changed = True

    if tom_doc and not processor.tom_exists:
        processor.tom_exists = True
        changed = True

    if changed:
        processor.save(update_fields=["av_contract_exists", "tom_exists", "updated_at"])

    return {
        "av_created": av_doc is not None,
        "tom_created": tom_doc is not None,
    }


def _catalog_update_required(processor):
    catalog = processor.catalog_entry
    if not catalog:
        return False

    has_av_doc = Document.objects.filter(
        related_processor=processor,
        document_type=Document.DocumentType.AV_CONTRACT,
    ).exists()

    has_tom_doc = Document.objects.filter(
        related_processor=processor,
        document_type=Document.DocumentType.TOM,
    ).exists()

    if catalog.standard_av_file and not has_av_doc:
        return True

    if catalog.standard_tom_file and not has_tom_doc:
        return True

    relevant_documents = Document.objects.filter(
        related_processor=processor,
        document_type__in=[
            Document.DocumentType.AV_CONTRACT,
            Document.DocumentType.TOM,
        ],
    )

    for document in relevant_documents:
        if document.source_catalog_updated_at and catalog.updated_at > document.source_catalog_updated_at:
            return True

    return False


def _ensure_catalog_update_action(processor):
    title = "AV/TOM-Dokumente prüfen und aktualisieren"

    existing = ActionItem.objects.filter(
        tenant=processor.tenant,
        related_processor=processor,
        title=title,
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
        ],
    ).first()

    if existing:
        return False

    ActionItem.objects.create(
        tenant=processor.tenant,
        related_processor=processor,
        title=title,
        description=(
            f"Für den Auftragsverarbeiter '{processor.name}' wurden fehlende oder aktualisierte "
            "AV-/TOM-Dokumente im Anbieter-Katalog erkannt.\n\n"
            "Bitte prüfen Sie, ob die Dokumente übernommen oder aktualisiert werden müssen."
        ),
        source_type=ActionItem.SourceType.PROCESSOR,
        source_area=ActionItem.Area.PROCESSOR,
        target_area=ActionItem.Area.DOCUMENT,
        priority=ActionItem.Priority.MEDIUM,
        status=ActionItem.Status.OPEN,
        responsible_person=processor.contact_person or "",
    )
    return True


@login_required
def processor_list(request):
    items = _tenant_filtered_processor_queryset(request)
    return render(request, "processors/list.html", {"items": items})


@login_required
def processor_create(request):
    if request.method == "POST":
        form = ProcessorForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)

            active_tenant = get_effective_tenant(request)
            if active_tenant is not None:
                item.tenant = active_tenant
            elif request.user.tenant_id:
                item.tenant = request.user.tenant

            item.save()
            form.save_m2m()

            copied = _copy_catalog_documents_to_tenant(item)

            if copied["av_created"] or copied["tom_created"]:
                copied_parts = []
                if copied["av_created"]:
                    copied_parts.append("AV")
                if copied["tom_created"]:
                    copied_parts.append("TOM")
                messages.info(
                    request,
                    "Standarddokumente aus dem Anbieter-Katalog übernommen: " + ", ".join(copied_parts)
                )

            messages.success(request, "Der Auftragsverarbeiter wurde erfolgreich angelegt.")
            return redirect("processor_detail", pk=item.pk)
    else:
        form = ProcessorForm()

    return render(
        request,
        "processors/form.html",
        {
            "form": form,
            "page_title": "Neuer Auftragsverarbeiter",
            "submit_label": "Speichern",
            "provider_catalog_payload": _get_provider_catalog_payload(),
        },
    )


@login_required
def processor_detail(request, pk):
    item = get_object_or_404(_tenant_filtered_processor_queryset(request), pk=pk)

    copied = _copy_catalog_documents_to_tenant(item)
    if copied["av_created"] or copied["tom_created"]:
        copied_parts = []
        if copied["av_created"]:
            copied_parts.append("AV")
        if copied["tom_created"]:
            copied_parts.append("TOM")
        messages.info(
            request,
            "Beim Öffnen wurden Standarddokumente aus dem Anbieter-Katalog übernommen: " + ", ".join(copied_parts)
        )

    av_contract_documents = Document.objects.filter(
        related_processor=item,
        document_type=Document.DocumentType.AV_CONTRACT,
    ).order_by("-created_at")

    tom_documents = Document.objects.filter(
        related_processor=item,
        document_type=Document.DocumentType.TOM,
    ).order_by("-created_at")

    catalog_update_required = _catalog_update_required(item)

    if catalog_update_required:
        action_created = _ensure_catalog_update_action(item)
        if action_created:
            messages.warning(
                request,
                "Neue Maßnahme: AV/TOM-Dokumente müssen aufgrund fehlender oder aktualisierter Katalogdaten geprüft werden."
            )

    return render(
        request,
        "processors/detail.html",
        {
            "item": item,
            "av_contract_documents": av_contract_documents,
            "latest_av_contract_document": av_contract_documents.first(),
            "tom_documents": tom_documents,
            "latest_tom_document": tom_documents.first(),
            "catalog_update_required": catalog_update_required,
        },
    )


@login_required
def processor_edit(request, pk):
    item = get_object_or_404(_tenant_filtered_processor_queryset(request), pk=pk)

    if request.method == "POST":
        form = ProcessorForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)

            if not item.tenant_id:
                active_tenant = get_effective_tenant(request)
                if active_tenant is not None:
                    item.tenant = active_tenant
                elif request.user.tenant_id:
                    item.tenant = request.user.tenant

            item.save()
            form.save_m2m()

            copied = _copy_catalog_documents_to_tenant(item)

            if copied["av_created"] or copied["tom_created"]:
                copied_parts = []
                if copied["av_created"]:
                    copied_parts.append("AV")
                if copied["tom_created"]:
                    copied_parts.append("TOM")
                messages.info(
                    request,
                    "Standarddokumente aus dem Anbieter-Katalog übernommen: " + ", ".join(copied_parts)
                )

            messages.success(request, "Der Auftragsverarbeiter wurde erfolgreich aktualisiert.")
            return redirect("processor_detail", pk=item.pk)
    else:
        form = ProcessorForm(instance=item)

    return render(
        request,
        "processors/form.html",
        {
            "form": form,
            "page_title": f"Auftragsverarbeiter bearbeiten: {item.name}",
            "submit_label": "Änderungen speichern",
            "item": item,
            "provider_catalog_payload": _get_provider_catalog_payload(),
        },
    )