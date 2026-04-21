from django.core.validators import FileExtensionValidator
from django.db import models


class KnowledgeCategory(models.TextChoices):
    LEGAL_GUIDANCE = "legal_guidance", "Rechtliche Leitlinie"
    DPIA_GUIDANCE = "dpia_guidance", "DSFA-Leitlinie"
    ASSESSMENT_SCHEME = "assessment_scheme", "Bewertungsschema"
    INTERNAL_POLICY = "internal_policy", "Interne Richtlinie"
    GENERAL = "general", "Allgemein"


class TemplateCategory(models.TextChoices):
    DATA_SUBJECT_RIGHTS = "data_subject_rights", "Betroffenenrechte"
    DATA_BREACH = "data_breach", "Datenschutzvorfall"
    INTERNAL_REQUEST = "internal_request", "Interne Anfrage"
    PROCESSOR_REQUEST = "processor_request", "Anfrage an Auftragsverarbeiter"
    DPIA = "dpia", "DSFA"
    GENERAL = "general", "Allgemein"


class TrustedSourceCategory(models.TextChoices):
    SUPERVISORY_AUTHORITY = "supervisory_authority", "Aufsichtsbehörde"
    PUBLIC_GUIDANCE = "public_guidance", "Öffentliche Leitlinie"
    LEGISLATION = "legislation", "Gesetzgebung"
    COURT = "court", "Gericht / Rechtsprechung"
    GENERAL = "general", "Allgemein"


class AnalyseTextTopic(models.TextChoices):
    LEGITIMATE_INTEREST = "legitimate_interest", "Interessenabwägung"
    DPIA = "dpia", "DSFA"
    LEGAL_ASSESSMENT = "legal_assessment", "Rechtsbewertung"
    TEMPLATE = "template", "Mustertext"
    GENERAL = "general", "Allgemein"


class KnowledgeFolder(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wissensordner"
        verbose_name_plural = "Wissensordner"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class AnalyseText(models.Model):
    folder = models.ForeignKey(
        KnowledgeFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analyse_texts",
    )
    title = models.CharField(max_length=255)
    topic = models.CharField(
        max_length=50,
        choices=AnalyseTextTopic.choices,
        default=AnalyseTextTopic.GENERAL,
    )
    description = models.TextField(blank=True)
    raw_text = models.TextField(
        help_text="Rohtext für interne Analyse und KI-Auswertung.",
    )
    ai_enabled = models.BooleanField(
        default=True,
        help_text="Die KI darf diesen Text bei themenbezogenen Auswertungen verwenden.",
    )
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Analysetext"
        verbose_name_plural = "Analysetexte"
        ordering = ["topic", "title"]

    def __str__(self):
        return self.title


class KnowledgeEntry(models.Model):
    folder = models.ForeignKey(
        KnowledgeFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_entries",
    )
    title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=KnowledgeCategory.choices,
        default=KnowledgeCategory.GENERAL,
    )
    summary = models.TextField(blank=True)
    content = models.TextField(
        blank=True,
        help_text="Textinhalt für die KI-Auswertung. Kann zusätzlich oder alternativ zur Datei gepflegt werden.",
    )
    source_note = models.CharField(
        max_length=255,
        blank=True,
        help_text="Interne Quelle oder Kurzvermerk, z. B. 'Kanzleistandard 2026'.",
    )
    file = models.FileField(
        upload_to="knowledge/entries/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["txt", "md", "docx", "pdf"])],
        help_text="Erlaubte Formate: txt, md, docx, pdf",
    )
    version = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    allowed_for_ai = models.BooleanField(
        default=True,
        help_text="Die KI darf diesen Eintrag verwenden.",
    )
    admin_only = models.BooleanField(
        default=True,
        help_text="Nur Admin sichtbar.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wissenseintrag"
        verbose_name_plural = "Wissenseinträge"
        ordering = ["category", "title"]

    def __str__(self):
        return self.title


class TextTemplate(models.Model):
    folder = models.ForeignKey(
        KnowledgeFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="text_templates",
    )
    title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=TemplateCategory.choices,
        default=TemplateCategory.GENERAL,
    )
    description = models.TextField(blank=True)
    template_text = models.TextField(
        blank=True,
        help_text="Mustertext für die KI oder für spätere manuelle Nutzung.",
    )
    file = models.FileField(
        upload_to="knowledge/templates/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["txt", "md", "docx", "pdf"])],
        help_text="Erlaubte Formate: txt, md, docx, pdf",
    )
    version = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    allowed_for_ai = models.BooleanField(
        default=True,
        help_text="Die KI darf diesen Mustertext verwenden.",
    )
    admin_only = models.BooleanField(
        default=True,
        help_text="Nur Admin sichtbar.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mustertext"
        verbose_name_plural = "Mustertexte"
        ordering = ["category", "title"]

    def __str__(self):
        return self.title


class TrustedSource(models.Model):
    folder = models.ForeignKey(
        KnowledgeFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trusted_sources",
    )
    title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=TrustedSourceCategory.choices,
        default=TrustedSourceCategory.GENERAL,
    )
    base_url = models.URLField(
        unique=True,
        help_text="Nur von dir freigegebene offizielle Quelle.",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    allowed_for_ai = models.BooleanField(
        default=True,
        help_text="Die KI darf diese Quelle ergänzend verwenden.",
    )
    admin_only = models.BooleanField(
        default=True,
        help_text="Nur Admin sichtbar.",
    )
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Niedriger Wert = höhere Priorität.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vertrauenswürdige Quelle"
        verbose_name_plural = "Vertrauenswürdige Quellen"
        ordering = ["priority", "title"]

    def __str__(self):
        return self.title