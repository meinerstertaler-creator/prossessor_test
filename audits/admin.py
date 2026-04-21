from django.contrib import admin

from .models import (
    Audit,
    AuditQuestion,
    AuditResponse,
    ProcedureAudit,
    ProcedureAuditChecklistResponse,
    ProcedureAuditItem,
)


@admin.register(AuditQuestion)
class AuditQuestionAdmin(admin.ModelAdmin):
    list_display = ("category", "question_text", "sort_order", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("question_text",)


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ("processor", "audit_year", "audit_type", "status", "overall_result")
    list_filter = ("audit_type", "status", "overall_result", "audit_year")
    search_fields = ("processor__name", "summary", "auditor_name")


@admin.register(AuditResponse)
class AuditResponseAdmin(admin.ModelAdmin):
    list_display = ("audit", "question", "rating", "evidence_available", "action_required")
    list_filter = ("rating", "evidence_available", "action_required")
    search_fields = ("audit__processor__name", "question__question_text", "comment")


@admin.register(ProcedureAudit)
class ProcedureAuditAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "tenant",
        "audit_year",
        "audit_type",
        "status",
        "execution_type",
        "overall_result",
        "is_archived",
    )
    list_filter = (
        "audit_type",
        "status",
        "execution_type",
        "overall_result",
        "is_archived",
        "audit_year",
    )
    search_fields = ("title", "tenant__name", "auditor_name", "participants", "summary")


@admin.register(ProcedureAuditItem)
class ProcedureAuditItemAdmin(admin.ModelAdmin):
    list_display = (
        "audit",
        "processing_activity",
        "review_status",
        "legal_review_required",
        "dpia_review_required",
        "action_required",
    )
    list_filter = (
        "review_status",
        "legal_review_required",
        "dpia_review_required",
        "action_required",
    )
    search_fields = ("audit__title", "processing_activity__title", "notes")


@admin.register(ProcedureAuditChecklistResponse)
class ProcedureAuditChecklistResponseAdmin(admin.ModelAdmin):
    list_display = ("procedure_audit", "question", "rating", "evidence_available", "action_required")
    list_filter = ("rating", "evidence_available", "action_required")
    search_fields = ("procedure_audit__title", "question__question_text", "comment")