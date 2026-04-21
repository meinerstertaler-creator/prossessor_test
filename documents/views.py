from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render

from accounts.models import Tenant
from core.tenant_utils import get_effective_tenant

from .models import Document, DocumentFolder, DocumentLabel


def _get_permitted_documents(request):
    qs = Document.objects.select_related(
        "tenant",
        "folder",
        "related_processing_activity",
        "related_legal_assessment",
        "related_processor",
        "related_audit",
        "related_action_item",
        "uploaded_by",
    ).prefetch_related("labels")

    if not request.user.is_superuser:
        tenant = request.user.tenant
        if tenant is None:
            return Document.objects.none()

        return qs.filter(
            Q(tenant=tenant)
            | Q(related_processing_activity__tenant=tenant)
            | Q(related_legal_assessment__tenant=tenant)
            | Q(related_processor__tenant=tenant)
            | Q(related_audit__tenant=tenant)
            | Q(related_action_item__tenant=tenant)
        ).distinct()

    active_tenant = get_effective_tenant(request)
    if active_tenant is not None:
        return qs.filter(
            Q(tenant=active_tenant)
            | Q(related_processing_activity__tenant=active_tenant)
            | Q(related_legal_assessment__tenant=active_tenant)
            | Q(related_processor__tenant=active_tenant)
            | Q(related_audit__tenant=active_tenant)
            | Q(related_action_item__tenant=active_tenant)
        ).distinct()

    return qs


def _get_effective_document_tenant_for_request(request, posted_tenant_id=None):
    if request.user.is_superuser:
        if posted_tenant_id:
            try:
                return Tenant.objects.get(pk=posted_tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                return None
        return get_effective_tenant(request)

    return request.user.tenant if request.user.tenant_id else None


def _get_available_folders_for_request(request):
    if request.user.is_superuser:
        active_tenant = get_effective_tenant(request)
        if active_tenant is not None:
            return DocumentFolder.objects.filter(
                tenant=active_tenant,
                is_active=True,
            ).order_by("name")
        return DocumentFolder.objects.filter(is_active=True).order_by("tenant__name", "name")

    if request.user.tenant_id:
        return DocumentFolder.objects.filter(
            tenant=request.user.tenant,
            is_active=True,
        ).order_by("name")

    return DocumentFolder.objects.none()


def _get_available_labels_for_request(request):
    if request.user.is_superuser:
        active_tenant = get_effective_tenant(request)
        if active_tenant is not None:
            return DocumentLabel.objects.filter(
                tenant=active_tenant,
                is_active=True,
            ).order_by("name")
        return DocumentLabel.objects.filter(is_active=True).order_by("tenant__name", "name")

    if request.user.tenant_id:
        return DocumentLabel.objects.filter(
            tenant=request.user.tenant,
            is_active=True,
        ).order_by("name")

    return DocumentLabel.objects.none()


def _build_upload_context(request, extra=None):
    context = {
        "document_types": Document.DocumentType.choices,
        "folders": _get_available_folders_for_request(request),
        "labels": _get_available_labels_for_request(request),
    }

    if request.user.is_superuser:
        context["tenants"] = Tenant.objects.filter(is_active=True).order_by("name")

    if extra:
        context.update(extra)

    return context


@login_required
def document_list(request):
    items = _get_permitted_documents(request)

    folder_id = (request.GET.get("folder") or "").strip()
    label_id = (request.GET.get("label") or "").strip()
    search = (request.GET.get("q") or "").strip()

    folders = _get_available_folders_for_request(request)
    labels = _get_available_labels_for_request(request)

    if folder_id:
        items = items.filter(folder_id=folder_id)

    if label_id:
        items = items.filter(labels__id=label_id)

    if search:
        items = items.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(version__icontains=search)
        )

    items = items.distinct().order_by("title")

    return render(
        request,
        "documents/list.html",
        {
            "items": items,
            "folders": folders,
            "labels": labels,
            "selected_folder": folder_id,
            "selected_label": label_id,
            "search": search,
        },
    )


@login_required
def document_download(request, pk):
    items = _get_permitted_documents(request)

    try:
        item = items.get(pk=pk)
    except Document.DoesNotExist:
        raise Http404("Dokument nicht gefunden.")

    if not item.file:
        raise Http404("Dokumentdatei nicht gefunden.")

    try:
        return FileResponse(
            item.file.open("rb"),
            as_attachment=False,
            filename=item.file.name.split("/")[-1],
        )
    except FileNotFoundError:
        raise Http404("Dokumentdatei nicht gefunden.")


@login_required
def document_upload(request):
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        document_type = (request.POST.get("document_type") or "").strip()
        file = request.FILES.get("file")
        version = (request.POST.get("version") or "").strip()
        description = (request.POST.get("description") or "").strip() or "N/A"
        folder_id = (request.POST.get("folder") or "").strip()
        label_ids = request.POST.getlist("labels")
        posted_tenant_id = (request.POST.get("tenant") or "").strip()

        if not title or not document_type or not file:
            messages.error(request, "Bitte alle Pflichtfelder ausfüllen.")
            return redirect("document_upload")

        document = Document(
            title=title,
            document_type=document_type,
            file=file,
            version=version,
            description=description,
            uploaded_by=request.user,
        )

        effective_tenant = _get_effective_document_tenant_for_request(request, posted_tenant_id)

        if request.user.is_superuser:
            if posted_tenant_id:
                if effective_tenant is None:
                    messages.error(request, "Der gewählte Mandant ist nicht zulässig.")
                    return redirect("document_upload")
                document.tenant = effective_tenant
        else:
            document.tenant = effective_tenant

        if folder_id:
            try:
                folder = _get_available_folders_for_request(request).get(pk=folder_id)
                document.folder = folder
            except DocumentFolder.DoesNotExist:
                messages.error(request, "Der gewählte Ordner ist nicht zulässig.")
                return redirect("document_upload")

        try:
            document.save()
        except Exception as exc:
            messages.error(request, f"Fehler beim Speichern: {exc}")
            return redirect("document_upload")

        if label_ids:
            valid_labels = _get_available_labels_for_request(request).filter(pk__in=label_ids)
            document.labels.set(valid_labels)

        messages.success(request, "Dokument erfolgreich hochgeladen.")
        return redirect("document_list")

    return render(request, "documents/upload.html", _build_upload_context(request))


@login_required
def document_folder_create(request):
    if request.method != "POST":
        return redirect("document_upload")

    posted_tenant_id = (request.POST.get("tenant") or "").strip()
    tenant = _get_effective_document_tenant_for_request(request, posted_tenant_id)

    if tenant is None:
        messages.error(request, "Es konnte kein Mandant für den neuen Ordner ermittelt werden.")
        return redirect("document_upload")

    name = (request.POST.get("folder_name") or "").strip()
    parent_id = (request.POST.get("folder_parent") or "").strip()

    if not name:
        messages.error(request, "Bitte einen Ordnernamen angeben.")
        return redirect("document_upload")

    parent = None
    if parent_id:
        try:
            parent = DocumentFolder.objects.get(pk=parent_id, tenant=tenant, is_active=True)
        except DocumentFolder.DoesNotExist:
            messages.error(request, "Der gewählte übergeordnete Ordner ist nicht zulässig.")
            return redirect("document_upload")

    folder, created = DocumentFolder.objects.get_or_create(
        tenant=tenant,
        name=name,
        parent=parent,
        defaults={"is_active": True},
    )

    if created:
        messages.success(request, f"Ordner „{folder}“ wurde angelegt.")
    else:
        messages.info(request, f"Ordner „{folder}“ war bereits vorhanden.")

    return redirect("document_upload")


@login_required
def document_label_create(request):
    if request.method != "POST":
        return redirect("document_upload")

    posted_tenant_id = (request.POST.get("tenant") or "").strip()
    tenant = _get_effective_document_tenant_for_request(request, posted_tenant_id)

    if tenant is None:
        messages.error(request, "Es konnte kein Mandant für das neue Label ermittelt werden.")
        return redirect("document_upload")

    name = (request.POST.get("label_name") or "").strip()

    if not name:
        messages.error(request, "Bitte einen Labelnamen angeben.")
        return redirect("document_upload")

    label, created = DocumentLabel.objects.get_or_create(
        tenant=tenant,
        name=name,
        defaults={"is_active": True},
    )

    if created:
        messages.success(request, f"Label „{label.name}“ wurde angelegt.")
    else:
        messages.info(request, f"Label „{label.name}“ war bereits vorhanden.")

    return redirect("document_upload")